from django.urls import path
from . import views

app_name = 'intranet'

urlpatterns = [
    # Vistas principales
    path('', views.dashboard_intranet, name='dashboard'),
    path('calendario/', views.calendario_reservas, name='calendario'),
    path('nueva-reserva/', views.nueva_reserva, name='nueva_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('reserva/<str:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('gestion-salas/', views.gestion_salas, name='gestion_salas'),
    
    # Endpoints API
    path('api/salas/', views.api_salas_disponibles, name='api_salas'),
    path('api/reservas/', views.api_obtener_reservas, name='api_reservas'),
    path('api/reservas/crear/', views.api_crear_reserva, name='api_crear_reserva'),
    path('api/reservas/cancelar/', views.api_cancelar_reserva, name='api_cancelar_reserva'),
    path('api/reservas/confirmar-asistencia/', views.api_confirmar_asistencia, name='api_confirmar_asistencia'),
    path('api/reservas/validar-conflicto/', views.api_validar_conflicto, name='api_validar_conflicto'),
    path('api/usuarios/', views.api_obtener_usuarios, name='api_usuarios'),
] 