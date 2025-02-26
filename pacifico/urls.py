from django.urls import path
from .views import fideicomiso_view, login_view, main_menu, get_lineas, cotizacion_seguro_auto, cotizacionesList, download_cotizaciones_excel,clientesList, view_active_sessions, terminate_all_sessions, download_merged_pdf
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView, CustomPasswordChangeDoneView
from .usuarios.vistasUsuarios import edit_profile
from django.conf import settings
from django.conf.urls.static import static
from .viewsFideicomiso.reportesExcel import generate_report
from .viewsPersonal.cotizadorPersonal import cotizacionPrestamoPersonal


urlpatterns = [
    path('', main_menu, name='main_menu'),
    path('cotizador/prestAuto/', fideicomiso_view, name='fideicomiso'),
    path('cotizador/prestPersonal/', cotizacionPrestamoPersonal, name='prestPersonal'),
    path('get_lineas/', views.get_lineas, name='get_lineas'),
    path('generate_report/<int:numero_cotizacion>/', generate_report, name='generate_report'),
    path('cotizacion_seguro_auto/', cotizacion_seguro_auto, name='cotizacion_seguro_auto'),
    path('cotizaciones/prestAuto/', cotizacionesList, name="cotizacionesList"),
    path('cotizaciones/descargar/', download_cotizaciones_excel, name='download_cotizaciones_excel'),
    path('cotizacion/<int:numero_cotizacion>/download/', download_merged_pdf, name='download_merged_pdf'),
    path('login/', login_view, name='login'),
    path('clientes/', clientesList, name="clientesList"),
    path('cliente/<str:cedula>/', views.cliente_profile, name='cliente_profile'),
    path('cotizacion/<int:pk>/', views.cotizacionDetail, name='cotizacion_detail'),
    path('aseguradora/new/', views.aseguradora_create, name='aseguradora_create'),
    path('aseguradoras/', views.aseguradora_list, name='aseguradora_list'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('active-sessions/', view_active_sessions, name='active_sessions'),
    path('terminate-sessions/', terminate_all_sessions, name='terminate_sessions'),
    path('usuario/editar/', edit_profile, name='edit_profile'),
    path('calculoAppx/', views.calculoAppx, name='calculoAppx'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
