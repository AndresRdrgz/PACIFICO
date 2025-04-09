from django.urls import path
from . import views

urlpatterns = [
    path('tombola/', views.moduloTombola, name='moduloTombola'),
    path('tombola/formulario/', views.formularioTombola, name='formularioTombola'),
]