from django.urls import path
from .views import fideicomiso_view, login_view, main_menu, get_lineas, cotizacion_seguro_auto, cotizacionesList, download_cotizaciones_excel, view_active_sessions, terminate_all_sessions, download_merged_pdf
from . import views
from . import viewsClientes
from . import viewsDebidaDiligencia
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView, CustomPasswordChangeDoneView
from .usuarios.vistasUsuarios import edit_profile
from django.conf import settings
from django.conf.urls.static import static
from .viewsFideicomiso.reportesExcel import generate_report,generate_report_pp
from .viewsPersonal.cotizadorPersonal import cotizacionPrestamoPersonal
from .viewsCotizadorAuto import cotizadorPrestAuto


urlpatterns = [
    path('', main_menu, name='main_menu'),
    path('cotizador/prestAuto/',cotizadorPrestAuto , name='fideicomiso'),
    path('cotizador/prestPersonal/', cotizacionPrestamoPersonal, name='prestPersonal'),  # No pk
    path('cotizador/prestPersonal/<int:pk>/', cotizacionPrestamoPersonal, name='prestPersonal_with_pk'),  # With pk
    path('cotizacionPP/', cotizacionPrestamoPersonal, name='cotizacionDetail_pp'),  # No pk
    path('cotizacionPP/<int:pk>/', cotizacionPrestamoPersonal, name='cotizacionDetail_pp_with_pk'),  # With pk
    path('get_lineas/', views.get_lineas, name='get_lineas'),
    path('generate_report/<int:numero_cotizacion>/', generate_report, name='generate_report'),
    path('generate_report_pp/<int:numero_cotizacion>/', generate_report_pp, name='generate_report_pp'),
    path('cotizacion_seguro_auto/', cotizacion_seguro_auto, name='cotizacion_seguro_auto'),
    path('cotizaciones/prestAuto/', cotizacionesList, name="cotizacionesList"),
    path('cotizaciones/descargar/', download_cotizaciones_excel, name='download_cotizaciones_excel'),
    path('cotizacion/<int:numero_cotizacion>/download/', download_merged_pdf, name='download_merged_pdf'),
    path('login/', login_view, name='login'),
    # Cliente CRUD
    path('clientes/create/', viewsClientes.cliente_create, name='cliente_create'),
    path('clientes/', viewsClientes.clientesList, name="clientesList"),
    path('cliente/<int:id>/', viewsClientes.cliente_profile, name='cliente_profile'),
    path('cotizacion/<int:pk>/', cotizadorPrestAuto, name='cotizacion_detail'),
    #path('cotizacionPP/<int:pk>/', cotizacionDetail_pp, name='cotizacionDetail_pp'),
    path('aseguradora/new/', views.aseguradora_create, name='aseguradora_create'),
    path('aseguradoras/', views.aseguradora_list, name='aseguradora_list'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('active-sessions/', view_active_sessions, name='active_sessions'),
    path('terminate-sessions/', terminate_all_sessions, name='terminate_sessions'),
    path('usuario/editar/', edit_profile, name='edit_profile'),
    path('calculoAppx/', views.calculoAppx, name='calculoAppx'),
    path('download_cotizaciones_json/', views.download_cotizaciones_json, name='download_cotizaciones_json'),

    # Debida Diligencia URLs
    path('debida-diligencia/solicitar/<int:cliente_id>/', viewsDebidaDiligencia.solicitar_debida_diligencia, name='solicitar_debida_diligencia'),
    path('debida-diligencia/upload/<int:diligencia_id>/', viewsDebidaDiligencia.debida_diligencia_upload, name='debida_diligencia_upload'),
    path('debida-diligencia/status/<int:cliente_id>/', viewsDebidaDiligencia.get_debida_diligencia_status, name='get_debida_diligencia_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
