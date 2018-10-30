from django import forms


class LogueoUsuario(forms.Form):
    usuario = forms.CharField(label='Usuario', max_length=64)
    clave = forms.CharField(widget=forms.PasswordInput())


class BuscadorForm(forms.Form):
    fecha_entrada = forms.CharField(label='Fecha llegada', max_length=10)
    fecha_salida = forms.CharField(label='Fecha salida', max_length=10)


class ReservarForm(forms.Form):
    tipo_tarjeta = forms.IntegerField()
    tarjeta_credito = forms.IntegerField()
    mes_expira = forms.IntegerField()
    anio_expira = forms.IntegerField()
    comentarios = forms.CharField(required=False)
