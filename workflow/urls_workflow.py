from django.urls import path
from django.views.static import serve
from django.conf import settings
from . import views_workflow
from . import views
import os

app_name = 'workflow'

urlpatterns = [
    # PWA routes
    path('manifest.json', views.manifest_view, name='manifest'),
    path('sw.js', views.service_worker_view, name='service_worker'),
    path('test-sw-debug/', views.test_service_worker, name='test_service_worker'),
    path('offline/', views_workflow.offline_view, name='offline'),
    path('api/health-check/', views_workflow.health_check, name='health_check'),
    path('pwa-test/', views_workflow.pwa_test_view, name='pwa_test'),
    
    # Alternative service worker route for debugging
] 

# Add static file serving for service worker in development
if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += [
        path('sw-static.js', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'workflow', 'static', 'workflow'),
            'path': 'sw.js'
        }, name='service_worker_static'),
    ]

# Vistas principales
urlpatterns += [
    path('', views_workflow.dashboard_workflow, name='dashboard'),
    path('bandeja/', views_workflow.bandeja_trabajo, name='bandeja_trabajo'),
    path('bandeja-mixta/', views_workflow.vista_mixta_bandejas, name='vista_mixta_bandejas'),
    path('negocios/', views_workflow.negocios_view, name='negocios'),
    path('nueva-solicitud/', views_workflow.nueva_solicitud, name='nueva_solicitud'),
    path('solicitud/<int:solicitud_id>/', views_workflow.detalle_solicitud, name='detalle_solicitud'),
    path('solicitud/<int:solicitud_id>/transicion/', views_workflow.transicion_solicitud, name='transicion_solicitud'),
    path('solicitud/<int:solicitud_id>/auto-asignar/', views_workflow.auto_asignar_solicitud, name='auto_asignar_solicitud'),
    path('solicitud/<int:solicitud_id>/requisito/<int:requisito_id>/actualizar/', views_workflow.actualizar_requisito, name='actualizar_requisito'),
    path('solicitud/<int:solicitud_id>/campos-personalizados/', views_workflow.actualizar_campo_personalizado, name='actualizar_campos_personalizados'),
    
    # APIs para bandeja mixta
    path('api/solicitudes/<int:solicitud_id>/tomar/', views_workflow.api_tomar_solicitud, name='api_tomar_solicitud'),
    path('api/solicitudes/<int:solicitud_id>/devolver/', views_workflow.api_devolver_solicitud, name='api_devolver_solicitud'),
    path('api/kpis/', views_workflow.api_kpis, name='api_kpis'),
    path('api/bandejas/', views_workflow.api_bandejas, name='api_bandejas'),
    path('api/notifications/stream/', views_workflow.api_notifications_stream, name='api_notifications_stream'),
    path('api/check-updates/', views_workflow.api_check_updates, name='api_check_updates'),
    path('api/get-updated-solicitudes/', views_workflow.api_get_updated_solicitudes, name='api_get_updated_solicitudes'),
    
    # Vistas de administración
    path('admin/pipelines/', views_workflow.administrar_pipelines, name='admin_pipelines'),
    path('admin/requisitos/', views_workflow.administrar_requisitos, name='admin_requisitos'),
    path('admin/campos-personalizados/', views_workflow.administrar_campos_personalizados, name='admin_campos_personalizados'),
    
    # Vistas de reportes
    path('reportes/', views_workflow.reportes_workflow, name='reportes'),
    
    # APIs
    path('api/solicitudes/', views_workflow.api_solicitudes, name='api_solicitudes'),
    path('api/estadisticas/', views_workflow.api_estadisticas, name='api_estadisticas'),
    
    # Páginas especiales
    path('construccion/', views_workflow.sitio_construccion, name='sitio_construccion'),
    
    # APIs para pipelines
    path('api/pipelines/crear/', views_workflow.api_crear_pipeline, name='api_crear_pipeline'),
    path('api/pipelines/<int:pipeline_id>/editar/', views_workflow.api_editar_pipeline, name='api_editar_pipeline'),
    path('api/pipelines/<int:pipeline_id>/eliminar/', views_workflow.api_eliminar_pipeline, name='api_eliminar_pipeline'),
    path('api/pipelines/<int:pipeline_id>/etapas/', views_workflow.api_obtener_etapas, name='api_obtener_etapas'),
    path('api/pipelines/<int:pipeline_id>/etapas/crear/', views_workflow.api_crear_etapa, name='api_crear_etapa'),
    path('api/etapas/<int:etapa_id>/editar/', views_workflow.api_editar_etapa, name='api_editar_etapa'),
    path('api/etapas/<int:etapa_id>/eliminar/', views_workflow.api_eliminar_etapa, name='api_eliminar_etapa'),
    path('api/etapas/<int:etapa_id>/subestados/crear/', views_workflow.api_crear_subestado, name='api_crear_subestado'),
    path('api/pipelines/<int:pipeline_id>/transiciones/crear/', views_workflow.api_crear_transicion, name='api_crear_transicion'),
    path('api/requisitos/crear/', views_workflow.api_crear_requisito, name='api_crear_requisito'),
    path('api/pipelines/<int:pipeline_id>/requisitos/asignar/', views_workflow.api_asignar_requisito_pipeline, name='api_asignar_requisito_pipeline'),
    path('api/pipelines/<int:pipeline_id>/campos-personalizados/crear/', views_workflow.api_crear_campo_personalizado, name='api_crear_campo_personalizado'),
    path('api/pipelines/<int:pipeline_id>/datos/', views_workflow.api_obtener_datos_pipeline, name='api_obtener_datos_pipeline'),
    # APIs para edición inline de solicitudes
    path('api/solicitudes/<int:solicitud_id>/actualizar-prioridad/', views_workflow.api_actualizar_prioridad, name='api_actualizar_prioridad'),
    path('api/solicitudes/<int:solicitud_id>/actualizar-etiquetas/', views_workflow.api_actualizar_etiquetas, name='api_actualizar_etiquetas'),
    
    # APIs para búsqueda de clientes y cotizaciones
    path('api/buscar-clientes/', views_workflow.api_buscar_clientes, name='api_buscar_clientes'),
    path('api/buscar-cotizaciones/', views_workflow.api_buscar_cotizaciones, name='api_buscar_cotizaciones'),
    
    # API para cambio de etapa
    path('api/solicitudes/<int:solicitud_id>/cambiar-etapa/', views_workflow.api_cambiar_etapa, name='api_cambiar_etapa'),
    path('api/solicitud_brief/<int:solicitud_id>/', views_workflow.api_solicitud_brief, name='api_solicitud_brief'),
    
    # APIs para validación de requisitos en transiciones
    path('api/solicitudes/<int:solicitud_id>/requisitos-transicion/', views_workflow.api_obtener_requisitos_transicion, name='api_obtener_requisitos_transicion'),
    path('api/solicitudes/<int:solicitud_id>/subir-requisito/', views_workflow.api_subir_requisito_transicion, name='api_subir_requisito_transicion'),
    path('api/solicitudes/<int:solicitud_id>/validar-requisitos/', views_workflow.api_validar_requisitos_antes_transicion, name='api_validar_requisitos_antes_transicion'),
    
    # APIs para gestión de requisitos de transición
    path('api/pipelines/<int:pipeline_id>/requisitos-transicion/', views_workflow.api_obtener_requisitos_transicion_pipeline, name='api_obtener_requisitos_transicion_pipeline'),
    path('api/requisitos-transicion/crear/', views_workflow.api_crear_requisito_transicion, name='api_crear_requisito_transicion'),
    path('api/requisitos-transicion/<int:requisito_transicion_id>/actualizar/', views_workflow.api_actualizar_requisito_transicion, name='api_actualizar_requisito_transicion'),
    path('api/requisitos-transicion/<int:requisito_transicion_id>/eliminar/', views_workflow.api_eliminar_requisito_transicion, name='api_eliminar_requisito_transicion'),
    
    # API para obtener transiciones válidas
    path('api/solicitudes/<int:solicitud_id>/transiciones-validas/', views_workflow.api_obtener_transiciones_validas, name='api_obtener_transiciones_validas'),
    
    # APIs para modal de requisitos faltantes
    path('api/solicitudes/<int:solicitud_id>/requisitos-faltantes-detallado/', views_workflow.api_obtener_requisitos_faltantes_detallado, name='api_obtener_requisitos_faltantes_detallado'),
    path('api/solicitudes/<int:solicitud_id>/subir-requisito-modal/', views_workflow.api_subir_requisito_modal, name='api_subir_requisito_modal'),
]
