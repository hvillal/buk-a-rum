from django.contrib import admin
from .models import TipoHabitacion, Habitacion, Reserva, TarjetaCredito


class ReservaAdmin(admin.ModelAdmin):
    list_display = ('fecha_entrada', 'fecha_salida', 'habitacion', )
    ordering = ('-fecha_entrada', '-fecha_salida', 'habitacion', )


admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(TarjetaCredito)
