# Generated by Django 2.1.2 on 2018-10-21 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buscador', '0003_auto_20181021_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserva',
            name='localizador',
            field=models.CharField(default=None, max_length=32),
        ),
    ]
