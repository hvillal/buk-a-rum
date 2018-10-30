from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('buscador/', views.buscador, name='buscador'),
    path('reservas/', views.mis_reservas, name='mis_reservas'),
    path('reservar/<int:id_tipo>/', views.reservar, name='reservar'),
    path('detalle/<int:id_reserva>/', views.detalle_reserva, name='detalle_reserva'),
    path('pdf/<int:id_reserva>/', views.pdf_reserva, name='pdf_reserva'),
    path('login/', views.iniciar, name='iniciar'),
    path('logout/', views.salir, name='salir'),
]
