# Generated by Django 2.1.2 on 2018-10-28 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buscador', '0005_auto_20181027_1844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reserva',
            name='nombres_tarjeta',
        ),
        migrations.RemoveField(
            model_name='reserva',
            name='numero_ccv',
        ),
    ]
