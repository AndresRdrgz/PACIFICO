from django.urls import path
from . import views
from . import api
from . import views_workflow

urlpatterns = [
    # URLs existentes del formulario de entrevista
    path('entrevista/', views.entrevista_cliente_view, name='entrevista_cliente'),
    path('gracias/', views.gracias, name='formulario_gracias'),
    path('entrevistas/', views.lista_entrevistas, name='lista_entrevistas'),
    path('descargar-entrevistas-excel/', views.descargar_entrevistas_excel, name='descargar_entrevistas_excel'),
    path('entrevistas/descargar/<int:entrevista_id>/', views.descargar_entrevista_excel, name='descargar_entrevista_excel'),
    path('entrevistas/json/', api.entrevistas_json, name='entrevistas_json'),
    
    # Workflow URLs
    path('', views_workflow.dashboard_workflow, name='dashboard'),
    path('negocios/', views_workflow.negocios_view, name='negocios'),
    path('bandeja-trabajo/', views_workflow.bandeja_trabajo, name='bandeja_trabajo'),
    path('nueva-solicitud/', views_workflow.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:solicitud_id>/detalle/', views_workflow.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:solicitud_id>/transicion/', views_workflow.transicion_solicitud, name='transicion_solicitud'),
    path('solicitudes/<int:solicitud_id>/auto-asignar/', views_workflow.auto_asignar_solicitud, name='auto_asignar_solicitud'),
    path('solicitudes/<int:solicitud_id>/requisitos/<int:requisito_id>/actualizar/', views_workflow.actualizar_requisito, name='actualizar_requisito'),
    path('solicitudes/<int:solicitud_id>/campos-personalizados/', views_workflow.actualizar_campo_personalizado, name='actualizar_campo_personalizado'),
    
    # Admin URLs
    path('admin/pipelines/', views_workflow.administrar_pipelines, name='admin_pipelines'),
    path('admin/requisitos/', views_workflow.administrar_requisitos, name='admin_requisitos'),
    path('admin/campos-personalizados/', views_workflow.administrar_campos_personalizados, name='admin_campos_personalizados'),
    path('reportes/', views_workflow.reportes_workflow, name='reportes'),
    
    # API URLs
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
    path('api/solicitudes/', views_workflow.api_solicitudes, name='api_solicitudes'),
    path('api/estadisticas/', views_workflow.api_estadisticas, name='api_estadisticas'),
    path('api/solicitudes/<int:solicitud_id>/prioridad/', views_workflow.api_actualizar_prioridad, name='api_actualizar_prioridad'),
    path('api/solicitudes/<int:solicitud_id>/etiquetas/', views_workflow.api_actualizar_etiquetas, name='api_actualizar_etiquetas'),
    path('api/buscar-clientes/', views_workflow.api_buscar_clientes, name='api_buscar_clientes'),
    path('api/buscar-cotizaciones/', views_workflow.api_buscar_cotizaciones, name='api_buscar_cotizaciones'),
    path('api/solicitudes/<int:solicitud_id>/cambiar-etapa/', views_workflow.api_cambiar_etapa, name='api_cambiar_etapa'),
    path('api/solicitudes/<int:solicitud_id>/tomar/', views_workflow.api_tomar_solicitud, name='api_tomar_solicitud'),
    path('api/solicitudes/<int:solicitud_id>/devolver/', views_workflow.api_devolver_solicitud, name='api_devolver_solicitud'),
    
    # Bandejas de trabajo URLs
    path('bandejas/', views_workflow.vista_mixta_bandejas, name='vista_mixta_bandejas'),
    path('api/kpis/', views_workflow.api_kpis, name='api_kpis'),
    path('api/bandejas/', views_workflow.api_bandejas, name='api_bandejas'),
    path('api/check-updates/', views_workflow.api_check_updates, name='api_check_updates'),
    path('api/notifications-stream/', views_workflow.api_notifications_stream, name='api_notifications_stream'),
    
    # Comments API URLs
    path('api/solicitudes/<int:solicitud_id>/comentarios/', views_workflow.api_obtener_comentarios, name='api_obtener_comentarios'),
    path('api/solicitudes/<int:solicitud_id>/comentarios/crear/', views_workflow.api_crear_comentario, name='api_crear_comentario'),
    path('api/comentarios/<int:comentario_id>/editar/', views_workflow.api_editar_comentario, name='api_editar_comentario'),
    path('api/comentarios/<int:comentario_id>/eliminar/', views_workflow.api_eliminar_comentario, name='api_eliminar_comentario'),
    
    # PDF Download API URLs
    path('api/solicitudes/<int:solicitud_id>/download-merged-pdf/', views_workflow.api_download_merged_pdf, name='api_download_merged_pdf'),
    
    # Field Califications API URLs
    path('api/solicitudes/<int:solicitud_id>/calificaciones/', api.api_obtener_calificaciones, name='api_obtener_calificaciones'),
    path('api/solicitudes/<int:solicitud_id>/calificaciones/calificar/', api.api_calificar_campo, name='api_calificar_campo'),
    path('api/solicitudes/<int:solicitud_id>/calificaciones/comentario/', api.api_comentario_compliance, name='api_comentario_compliance'),
    
    # Analista de Crédito API URLs
    path('api/solicitudes/<int:solicitud_id>/comentario-analista-credito/', api.api_comentario_analista_credito, name='api_comentario_analista_credito'),
    path('api/solicitudes/<int:solicitud_id>/comentarios-analista-credito/', api.api_obtener_comentarios_analista_credito, name='api_obtener_comentarios_analista_credito'),
    
    # Solicitud brief API (needed for modal)
    path('api/solicitud_brief/<int:solicitud_id>/', views_workflow.api_solicitud_brief, name='api_solicitud_brief'),
    
    # Solicitud detalle API (comprehensive data for detail view)
    path('api/solicitudes/<int:solicitud_id>/detalle/', views_workflow.api_solicitud_detalle, name='api_solicitud_detalle'),
    
    # Test API for solicitud detalle
    path('api/solicitudes/<int:solicitud_id>/test-detalle/', views_workflow.api_test_solicitud_detalle, name='api_test_solicitud_detalle'),
    
    # Drawer API URLs
    path('api/buscar-cotizaciones-drawer/', views_workflow.api_buscar_cotizaciones_drawer, name='api_buscar_cotizaciones_drawer'),
    path('api/buscar-clientes-drawer/', views_workflow.api_buscar_clientes_drawer, name='api_buscar_clientes_drawer'),
    path('api/formulario-datos/', views_workflow.api_formulario_datos, name='api_formulario_datos'),
    
    # Test temporal - eliminar después
    path('test-correo-bandeja/', views_workflow.test_envio_correo_bandeja, name='test_envio_correo_bandeja'),
    
    # Comité API URLs
    path('api/comite/niveles/', views_workflow.api_obtener_niveles_comite, name='api_obtener_niveles_comite'),
    path('api/comite/niveles/crear/', views_workflow.api_crear_nivel_comite, name='api_crear_nivel_comite'),
    path('api/comite/niveles/<int:nivel_id>/actualizar/', views_workflow.api_actualizar_nivel_comite, name='api_actualizar_nivel_comite'),
    path('api/comite/niveles/<int:nivel_id>/eliminar/', views_workflow.api_eliminar_nivel_comite, name='api_eliminar_nivel_comite'),
    path('api/comite/asignaciones/', views_workflow.api_obtener_asignaciones_comite, name='api_obtener_asignaciones_comite'),
    path('api/comite/asignaciones/crear/', views_workflow.api_asignar_usuario_nivel_comite, name='api_asignar_usuario_nivel_comite'),
    path('api/comite/asignaciones/<int:asignacion_id>/estado/', views_workflow.api_cambiar_estado_asignacion_comite, name='api_cambiar_estado_asignacion_comite'),
    path('api/comite/asignaciones/<int:asignacion_id>/eliminar/', views_workflow.api_eliminar_asignacion_comite, name='api_eliminar_asignacion_comite'),
    path('api/comite/usuarios-disponibles/', views_workflow.api_obtener_usuarios_disponibles_comite, name='api_obtener_usuarios_disponibles_comite'),
    path('api/comite/usuarios/<int:usuario_id>/niveles/<int:nivel_id>/desasignar/', views_workflow.api_desasignar_usuario_nivel_comite, name='api_desasignar_usuario_nivel_comite'),
    path('api/comite/estadisticas/', views_workflow.api_estadisticas_comite, name='api_estadisticas_comite'),
    path('api/usuarios/', views_workflow.api_obtener_usuarios, name='api_obtener_usuarios'),
    
    # Debug URLs
    path('api/debug-session/', views_workflow.debug_session, name='debug_session'),
]
