from django.urls import path
from . import views

urlpatterns = [
    path("moduloMantenimiento/", views.moduloMantenimiento, name="moduloMantenimiento"),
    path("cargaPatronos/", views.cargaPatronos, name="cargaPatronos"),
    path("cargaAgencias/", views.cargaAgencias, name="cargaAgencias"),
]