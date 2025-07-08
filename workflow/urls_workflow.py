from django.urls import path
from . import views_workflow

app_name = 'workflow'

urlpatterns = [
    # Vistas principales
    path('', views_workflow.dashboard_workflow, name='dashboard'),
    path('bandeja/', views_workflow.bandeja_trabajo, name='bandeja_trabajo'),
    path('negocios/', views_workflow.negocios_view, name='negocios'),
    path('nueva-solicitud/', views_workflow.nueva_solicitud, name='nueva_solicitud'),
    path('solicitud/<int:solicitud_id>/', views_workflow.detalle_solicitud, name='detalle_solicitud'),
    path('solicitud/<int:solicitud_id>/transicion/', views_workflow.transicion_solicitud, name='transicion_solicitud'),
    path('solicitud/<int:solicitud_id>/auto-asignar/', views_workflow.auto_asignar_solicitud, name='auto_asignar_solicitud'),
    path('solicitud/<int:solicitud_id>/requisito/<int:requisito_id>/actualizar/', views_workflow.actualizar_requisito, name='actualizar_requisito'),
    path('solicitud/<int:solicitud_id>/campos-personalizados/', views_workflow.actualizar_campo_personalizado, name='actualizar_campos_personalizados'),
    
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
] 