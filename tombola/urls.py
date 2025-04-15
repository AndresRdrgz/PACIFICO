from django.urls import path
from . import views, api

urlpatterns = [
    path('tombola/', views.moduloTombola, name='moduloTombola'),
    path('tombola/formulario/', views.formularioTombola, name='formularioTombola'),
    path('tombola/confirmacion/<int:boleto_id>/', views.confirmacion, name='confirmacion'),  # New confirmation URL
    path('tombola/validadorCedula/', views.validadorCedula, name='validadorCedula'),
    path('api/boletos/', api.fetch_boletos_by_cedula, name='fetch_boletos_by_cedula'),
    path('descargar-plantilla/', api.descargar_plantilla, name='descargar_plantilla'),
    path('carga-masiva/', api.carga_masiva, name='carga_masiva'),
]