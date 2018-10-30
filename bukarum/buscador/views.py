from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .forms import LogueoUsuario, BuscadorForm, ReservarForm
from .models import Reserva, Habitacion, TipoHabitacion, TarjetaCredito
from datetime import date, datetime
from weasyprint import HTML
import random
import string


def convierte_fecha_amd(fecha):
    """
    Convierte fecha formato DD-MM-AAAA a AAAA-MM-DD

    :param fecha:
    :return: fecha formato AAAA-MM-DD, o None en caso de tener un formato inesperado
    """
    try:
        fecha = date(int(fecha[-4:]), int(fecha[3:5]), int(fecha[:2]))
    except:
        return None

    return fecha


def noches(fecha_entrada, fecha_salida):
    """
    Función que retorna el número de noches según fechas de entrada y salida

    :param fecha_entrada: fecha de entrada
    :param fecha_salida: fecha de salida
    :return: número de noches de acuerdo al intervalo de fechas
    """
    numero_noches = (fecha_salida - fecha_entrada).days
    return numero_noches


def noches_str(fecha_entrada, fecha_salida):
    """
    Retorna el número de noches según fechas de entrada y salida

    :param fecha_entrada: fecha de entrada
    :param fecha_salida: fecha de salida
    :return: número de noches de acuerdo al intervalo de fechas
    """
    numero_noches = noches(fecha_entrada, fecha_salida)
    return str(numero_noches) + ' noches' if numero_noches > 1 else str(numero_noches) + ' noche'


def habitacion_disponible(id_tipo, fecha_entrada, fecha_salida):
    """
    Retorna una habitación disponible para el tipo y fechas seleccionadas

    :param id_tipo: tipo de habitación
    :param fecha_entrada: fecha de entrada
    :param fecha_salida: fecha de salida
    :return: habitación disponible, o None en caso de no cumplir con el criterio
    """
    try:
        habitacion = Habitacion.objects.filter(tipo__id=id_tipo).\
                                        exclude(reserva__fecha_entrada__lte=fecha_salida,
                                                reserva__fecha_salida__gte=fecha_entrada)[:1].get()
    except:
        return None

    return habitacion


def numero_localizador():
    """
    Generador de número de reserva

    :return: localizador
    """
    caracteres = string.ascii_letters + string.digits
    localizador = "".join(random.choice(caracteres) for _ in range(random.randint(8, 16)))

    return localizador


def busca_reserva(request, id_reserva):
    """
    Retorna una reserva por id, y valida que corresponda al usuario logueado

    :param id_reserva: pk de la reserva
    :return: reserva, o None en caso de no cumplir con el criterio
    """
    try:
        reserva = Reserva.objects.get(pk=id_reserva, usuario=request.user)
    except Reserva.DoesNotExist:
        reserva = None

    return reserva


def index(request):
    """
    Página principal del buscador de habitaciones
    """
    form = BuscadorForm()
    return render(request, 'index.html', {'form': form,
                                           'titulo': 'Buk-A-Rum',
                                           'cabecera': 'Bienvenido'})


@login_required(login_url='/login/')
def reservar(request, id_tipo):
    """
    Página para crear la reserva
    """
    fechas = {}
    try:
        fechas['entrada'] = datetime.strptime(request.session['fecha_entrada'], '%Y-%m-%d').date()
        fechas['salida'] = datetime.strptime(request.session['fecha_salida'], '%Y-%m-%d').date()
    except:
        return redirect('/')

    habitacion = habitacion_disponible(id_tipo, fechas['entrada'], fechas['salida'])
    if habitacion is None:
        return render(request, 'error.html', {'mensaje': 'Lo sentimos, no se encuentran habitaciones disponibles para las fechas seleccionadas'})

    if request.method == 'POST':
        form = ReservarForm(request.POST)
        if form.is_valid():
            tipo_tarjeta = form.cleaned_data['tipo_tarjeta']
            tarjeta_credito = form.cleaned_data['tarjeta_credito']
            mes_expira = form.cleaned_data['mes_expira']
            anio_expira = form.cleaned_data['anio_expira']
            comentarios = form.cleaned_data['comentarios'][:500]

            try:
                tarjeta = TarjetaCredito.objects.get(pk=tipo_tarjeta)
            except:
                return render(request, 'error.html', {
                    'mensaje': 'Ha seleccionado un tipo de tarjeta inválida'})

            Reserva(usuario=request.user, localizador=numero_localizador(),
                    fecha_entrada=fechas['entrada'], fecha_salida=fechas['salida'],
                    tipo_tarjeta=tarjeta, tarjeta_credito=tarjeta_credito,
                    mes_expira=mes_expira, anio_expira=anio_expira,
                    comentarios=comentarios, habitacion=habitacion,
                    fecha_reserva=datetime.now(),
                    precio_noche=habitacion.tipo.precio).save()

            return redirect(mis_reservas)
        else:
            error = form.errors
            return HttpResponse(error)
    else:
        anio = datetime.now().year
        form = ReservarForm()
        tarjetas = TarjetaCredito.objects.all()
        anios = range(anio, anio + 5)
        numero_noches = noches(fechas['entrada'], fechas['salida'])

        fechas['numero_noches'] = numero_noches
        fechas['precio_total'] = habitacion.tipo.precio * numero_noches

        return render(request, 'reservar.html', {'form': form,
                                                 'fechas': fechas,
                                                 'habitacion': habitacion,
                                                 'tarjetas': tarjetas,
                                                 'anios': anios
                                                 })


def detalle_reserva(request, id_reserva):
    """
    Página para visualizar el detalle de la reserva
    """
    reserva = busca_reserva(request, id_reserva)

    if reserva is None:
        return redirect('/')

    return render(request, 'detalle_reserva.html', {'reserva': reserva})


def pdf_reserva(request, id_reserva):
    """
    Página con formato para impresión pdf con detalle de la reserva
    """
    reserva = busca_reserva(request, id_reserva)

    if reserva is None:
        return redirect('/')

    reserva_html = render_to_string('pdf_reserva.html', {'reserva': reserva})
    html = HTML(string=reserva_html)
    result = html.write_pdf()

    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = 'filename=reserva_bukarum.pdf'

    return response


def mis_reservas(request):
    """
    Lista las reservas que tenga el usuario registrado en la base
    """
    lista_reservas = Reserva.objects.filter(usuario__username=request.user)
    if lista_reservas is not None:
        return render(request, 'reservas.html', {'reservas': lista_reservas})
    else:
        return render(request, 'error.html', {'mensaje': 'No tienes ninguna reserva registrada hasta ahora...'})


def buscador(request):
    """
    Lista las habitaciones disponibles para el intervalo seleccionado por el usuario
    """
    fechas = {}

    try:
        del request.session['fecha_entrada']
        del request.session['fecha_salida']
    except:
        pass

    if request.method == 'POST':
        form = BuscadorForm(request.POST)
        if form.is_valid():
            fe = form.cleaned_data['fecha_entrada']
            fs = form.cleaned_data['fecha_salida']
            fecha_entrada = convierte_fecha_amd(fe)
            fecha_salida = convierte_fecha_amd(fs)

            if fecha_entrada is None or fecha_salida is None:
                return render(request, 'error.html', {'mensaje': 'Error en formato de fecha'})

            fechas['entrada'] = fecha_entrada
            fechas['salida'] = fecha_salida
            fechas['noches'] = noches(fecha_entrada, fecha_salida)

            request.session['fecha_entrada'] = str(fecha_entrada)
            request.session['fecha_salida'] = str(fecha_salida)

            # Habitaciones disponibles
            habitaciones = Habitacion.objects.exclude(
                                reserva__fecha_entrada__lte=fecha_salida,
                                reserva__fecha_salida__gte=fecha_entrada)

            # tipos de habitaciones disponibles
            disponibles = TipoHabitacion.objects.filter(pk__in=[habitacion.tipo.id for habitacion in habitaciones])
    else:
        return redirect('/')

    return render(request, 'habitaciones.html', {'fechas': fechas, 'disponibles': disponibles})


def iniciar(request):
    """
    Inicio de sesión
    """
    data_login = {}
    if request.method == 'POST':
        form = LogueoUsuario(request.POST)
        if form.is_valid():
            u = form.cleaned_data['usuario']
            p = form.cleaned_data['clave']
            usuario = authenticate(username=u, password=p)
            if usuario is not None:
                if usuario.is_active:
                    login(request, usuario)
                    return redirect('/')
                else:
                    data_login = {'sesion': '¡Cuenta deshabilitada!'}
            else:
                data_login = {'sesion': '¡Usuario o clave incorrecta!'}
        else:
            data_login = {'sesion': 'Error general'}
    else:
        if not request.user.is_authenticated:
            form = LogueoUsuario()
            return render(request, 'login.html', {'form': form})
        else:
            return redirect('/')

    return render(request, 'login.html', data_login)


def salir(request):
    """
    Cierre de sesión
    """
    logout(request)
    return redirect('/')
