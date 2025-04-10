from django.urls import path
from . import views

urlpatterns = [
    path('tombola/', views.moduloTombola, name='moduloTombola'),
    path('tombola/formulario/', views.formularioTombola, name='formularioTombola'),
    path('tombola/confirmacion/<int:boleto_id>/', views.confirmacion, name='confirmacion'),  # New confirmation URL
]