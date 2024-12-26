from django.urls import path
from .views import fideicomiso_view, login_view, main_menu, get_lineas, generate_report, cotizacion_seguro_auto, cotizacionesList, download_cotizaciones_excel,clientesList
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView, CustomPasswordChangeDoneView


urlpatterns = [
    path('', main_menu, name='main_menu'),
    path('cotizador/prestAuto/', fideicomiso_view, name='fideicomiso'),
    path('get_lineas/', views.get_lineas, name='get_lineas'),
    path('generate_report/', generate_report, name='generate_report'),
    path('cotizacion_seguro_auto/', cotizacion_seguro_auto, name='cotizacion_seguro_auto'),
    path('cotizaciones/prestAuto/', cotizacionesList, name="cotizacionesList"),
    path('cotizaciones/descargar/', download_cotizaciones_excel, name='download_cotizaciones_excel'),
    path('login/', login_view, name='login'),
    path('clientes/', clientesList, name="clientesList"),
    path('cliente/<str:cedula>/', views.cliente_profile, name='cliente_profile'),
    path('cotizacion/<int:pk>/', views.cotizacion_detail, name='cotizacion_detail'),
    path('aseguradora/new/', views.aseguradora_create, name='aseguradora_create'),
    path('aseguradoras/', views.aseguradora_list, name='aseguradora_list'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
]