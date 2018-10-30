from django.db import models
from django.contrib.auth.models import User


class TipoHabitacion(models.Model):
    nombre = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name_plural = 'Tipo de habitaciones'

    def __str__(self):
        return 'Habitación {}'.format(self.nombre)


class Habitacion(models.Model):
    numero = models.IntegerField()
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return '{} - {}'.format(str(self.numero).zfill(2), self.tipo.nombre[:1])


class TarjetaCredito(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Tarjetas de crédito'

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    localizador = models.CharField(max_length=32)
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    tipo_tarjeta = models.ForeignKey(TarjetaCredito, on_delete=models.CASCADE)
    tarjeta_credito = models.IntegerField()
    mes_expira = models.IntegerField()
    anio_expira = models.IntegerField()
    comentarios = models.CharField(max_length=500, null=True, blank=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    precio_noche = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return '{} - Del {} al {}'.format(self.habitacion.tipo.nombre, self.fecha_entrada, self.fecha_salida)

    def numero_noches(self):
        return (self.fecha_salida - self.fecha_entrada).days

    def precio_total(self):
        return self.precio_noche * self.numero_noches()
