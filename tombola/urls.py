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
    path('download-formularios-excel/', api.download_formularios_excel, name='download_formularios_excel'),
    path('download-boletos-excel/', api.download_boletos_excel, name='download_boletos_excel'),
    path('download_boleto/<int:boleto_id>/', views.download_boleto, name='download_boleto'),
    path('send_boleto_email/<int:boleto_id>/', views.send_boleto_email, name='send_boleto_email'),
    path('api/boletos/listar/', api.listar_boletos, name='listar_boletos'),
    path('api/formularios/listar/', api.listar_formularios, name='listar_formularios'),
]

