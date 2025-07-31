from django.urls import path
from . import views
from . import api
from . import views_workflow
from . import views_negocios
from . import dashboard_views
from . import views_calificacion
from . import views_formulario
from . import views_comite
from . import apicomite
from . import views_reconsideraciones
#from . import api_appx_conexion

urlpatterns = [
    # URLs existentes del formulario de entrevista
    path('entrevista/', views_formulario.entrevista_cliente_view, name='entrevista_cliente'),
    path('entrevistas/admin/<int:entrevista_id>/', views_formulario.entrevista_admin_view, name='entrevista_admin'),
    path('gracias/', views_formulario.gracias, name='formulario_gracias'),
    path('entrevistas/', views_formulario.lista_entrevistas, name='lista_entrevistas'),
    path('descargar-entrevistas-excel/', views_formulario.descargar_entrevistas_excel, name='descargar_entrevistas_excel'),
    path('entrevistas/descargar/<int:entrevista_id>/', views_formulario.descargar_entrevista_excel, name='descargar_entrevista_excel'),
    path('entrevistas/pdf/<int:entrevista_id>/', views_formulario.descargar_entrevista_pdf, name='descargar_entrevista_pdf'),
    path('entrevistas/json/', api.entrevistas_json, name='entrevistas_json'),
    
    # APPX Core Integration APIs
    #path('api/entrevistas/<int:entrevista_id>/enviar-appx/', api_appx_conexion.enviar_entrevista_a_appx, name='enviar_entrevista_appx'),
    #path('api/appx/verificar-conexion/', api_appx_conexion.verificar_conexion_appx, name='verificar_conexion_appx'),
    
    # Workflow URLs
    path('', dashboard_views.dashboard_operativo, name='dashboard'),
    path('negocios/', views_negocios.negocios_view, name='negocios'),
    
    # Makito Tracking URLs
    path('makito-tracking/', views_workflow.makito_tracking_view, name='makito_tracking'),
    path('apc-tracking/', views_workflow.apc_tracking_view, name='apc_tracking'),
    path('sura-tracking/', views_workflow.sura_tracking_view, name='sura_tracking'),
    path('bandeja-trabajo/', views_workflow.bandeja_trabajo, name='bandeja_trabajo'),
    path('nueva-solicitud/', views_workflow.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:solicitud_id>/detalle/', views_workflow.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:solicitud_id>/backoffice/', views_workflow.detalle_solicitud, name='detalle_solicitud_backoffice'),
    path('solicitudes/<int:solicitud_id>/transicion/', views_workflow.transicion_solicitud, name='transicion_solicitud'),
    path('solicitudes/<int:solicitud_id>/auto-asignar/', views_workflow.auto_asignar_solicitud, name='auto_asignar_solicitud'),
    path('solicitudes/<int:solicitud_id>/requisitos/<int:requisito_id>/actualizar/', views_workflow.actualizar_requisito, name='actualizar_requisito'),
    path('solicitudes/<int:solicitud_id>/campos-personalizados/', views_workflow.actualizar_campo_personalizado, name='actualizar_campo_personalizado'),
    
    # Reconsideración URLs
    path('solicitud/<int:solicitud_id>/reconsideracion/solicitar/', views_reconsideraciones.solicitar_reconsideracion, name='solicitar_reconsideracion'),
    path('api/cotizaciones-cliente/<int:solicitud_id>/', views_reconsideraciones.api_cotizaciones_cliente, name='api_cotizaciones_cliente'),
    
    # Admin URLs
    path('admin/pipelines/', views_workflow.administrar_pipelines, name='admin_pipelines'),
    path('admin/requisitos/', views_workflow.administrar_requisitos, name='admin_requisitos'),
    path('admin/campos-personalizados/', views_workflow.administrar_campos_personalizados, name='admin_campos_personalizados'),
    
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
    path('api/solicitudes/', views_negocios.api_solicitudes, name='api_solicitudes'),
    path('api/estadisticas/', views_negocios.api_estadisticas, name='api_estadisticas'),
    path('api/solicitudes-tabla/', views_negocios.api_solicitudes_tabla, name='api_solicitudes_tabla'),
    path('api/solicitudes/<int:solicitud_id>/detalle-modal/', views_negocios.api_detalle_solicitud_modal, name='api_detalle_solicitud_modal'),
    path('api/estadisticas-negocios/', views_negocios.api_estadisticas_negocios, name='api_estadisticas_negocios'),
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
    
    # Subestados and Transiciones API URLs
    path('api/subestados-disponibles/<int:solicitud_id>/', views_workflow.api_subestados_disponibles, name='api_subestados_disponibles'),
    path('api/transiciones-disponibles/<int:solicitud_id>/', views_workflow.api_transiciones_disponibles, name='api_transiciones_disponibles'),
    path('api/avanzar-subestado/', views_workflow.api_avanzar_subestado, name='api_avanzar_subestado'),
    path('api/ejecutar-transicion/', views_workflow.api_ejecutar_transicion, name='api_ejecutar_transicion'),
    path('api/devolver-bandeja-grupal/', views_workflow.api_devolver_bandeja_grupal, name='api_devolver_bandeja_grupal'),
    
    # PDF Download API URLs
    path('api/solicitudes/<int:solicitud_id>/download-merged-pdf/', views_workflow.api_download_merged_pdf, name='api_download_merged_pdf'),
    path('api/solicitudes/<int:solicitud_id>/pdf-resultado-consulta/', views_workflow.api_pdf_resultado_consulta, name='api_pdf_resultado_consulta'),
    path('api/solicitudes/<int:solicitud_id>/pdf-resultado-comite/', views_workflow.api_pdf_resultado_comite, name='api_pdf_resultado_comite'),
    
    # Field Califications API URLs
    path('api/solicitudes/<int:solicitud_id>/calificaciones/', api.api_obtener_calificaciones, name='api_obtener_calificaciones'),
    path('api/solicitudes/<int:solicitud_id>/calificaciones/calificar/', api.api_calificar_campo, name='api_calificar_campo'),
    path('api/solicitudes/<int:solicitud_id>/calificaciones/comentario/', api.api_comentario_compliance, name='api_comentario_compliance'),
    
    # Analista de Crédito API URLs
    path('api/solicitudes/<int:solicitud_id>/comentarios-analista/', api.api_obtener_comentarios_analista_credito, name='api_obtener_comentarios_analista_credito'),
    path('api/solicitudes/<int:solicitud_id>/comentarios-analista/crear/', api.api_comentario_analista_credito, name='api_comentario_analista_credito'),
    
    # Notas y Recordatorios API URLs
    path('api/notas-recordatorios/<int:solicitud_id>/', api.api_notas_recordatorios_list, name='api_notas_recordatorios_list'),
    path('api/notas-recordatorios/<int:solicitud_id>/<int:nota_id>/', api.api_notas_recordatorios_detail, name='api_notas_recordatorios_detail'),
    path('api/notas-recordatorios/<int:solicitud_id>/crear/', api.api_notas_recordatorios_create, name='api_notas_recordatorios_create'),
    path('api/notas-recordatorios/<int:solicitud_id>/<int:nota_id>/actualizar/', api.api_notas_recordatorios_update, name='api_notas_recordatorios_update'),
    path('api/notas-recordatorios/<int:solicitud_id>/<int:nota_id>/eliminar/', api.api_notas_recordatorios_delete, name='api_notas_recordatorios_delete'),
    path('api/notas-recordatorios/<int:solicitud_id>/<int:nota_id>/completar/', api.api_notas_recordatorios_completar, name='api_notas_recordatorios_completar'),
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
    
    # Comité View URLs (add these to resolve 404 error)
    path('comite/', views_comite.bandeja_comite_view, name='bandeja_comite'),
    path('comite/debug/', views_comite.debug_bandeja_comite_view, name='debug_bandeja_comite'),
    path('comite/solicitud/<int:solicitud_id>/', views_comite.detalle_solicitud_comite, name='detalle_solicitud_comite'),
    
    # Additional Comité API URLs (from apicomite)
    path('api/comite/solicitudes/', apicomite.api_solicitudes_comite, name='api_solicitudes_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/participar/', apicomite.api_participar_comite, name='api_participar_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/escalar/', apicomite.api_escalar_comite, name='api_escalar_comite'),
    path('api/comite/niveles-usuario/', apicomite.api_niveles_usuario_comite, name='api_niveles_usuario_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/historial/', apicomite.api_historial_participaciones, name='api_historial_participaciones'),
    path('api/comite/solicitudes/<int:solicitud_id>/etapas-disponibles/', apicomite.api_etapas_disponibles_comite, name='api_etapas_disponibles_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/avanzar-etapa/', apicomite.api_avanzar_etapa_comite, name='api_avanzar_etapa_comite'),
    
    # URLs para calificación de documentos
    path('api/documento/calificar/', views_calificacion.calificar_documento, name='calificar_documento'),
    path('api/documento/comentar/', views_calificacion.comentar_documento, name='comentar_documento'),
    path('api/documento/comentario/editar/', views_calificacion.editar_comentario, name='editar_comentario'),
    path('api/documento/<int:requisito_solicitud_id>/comentarios/', views_calificacion.obtener_comentarios_documento, name='obtener_comentarios_documento'),
    path('api/documento/<int:requisito_solicitud_id>/calificaciones/', views_calificacion.obtener_calificaciones_documento, name='obtener_calificaciones_documento'),
    
    # URLs para asociación de entrevistas
    path('buscar-entrevistas/', views_workflow.buscar_entrevistas, name='buscar_entrevistas'),
    path('asociar-entrevista/', views_workflow.asociar_entrevista, name='asociar_entrevista'),
    
    # Debida Diligencia API URLs
    path('api/debida-diligencia/status/<int:solicitud_id>/', views_workflow.api_debida_diligencia_status, name='api_debida_diligencia_status'),
    path('api/debida-diligencia/solicitar/<int:solicitud_id>/', views_workflow.api_debida_diligencia_solicitar, name='api_debida_diligencia_solicitar'),
    path('api/debida-diligencia/solicitar-makito/<int:solicitud_id>/', views_workflow.api_debida_diligencia_solicitar_makito, name='api_debida_diligencia_solicitar_makito'),
    path('api/debida-diligencia/upload/<int:solicitud_id>/', views_workflow.api_debida_diligencia_upload, name='api_debida_diligencia_upload'),
    path('api/debida-diligencia/reenviar-correo/<int:solicitud_id>/', views_workflow.api_debida_diligencia_reenviar_correo, name='api_debida_diligencia_reenviar_correo'),
    path('api/debida-diligencia-tracking/', views_workflow.api_debida_diligencia_tracking, name='api_debida_diligencia_tracking'),
    
    # APC Makito Tracking API URLs
    path('api/apc/list/', views_workflow.api_apc_list, name='api_apc_list'),
    path('api/apc/detail/<str:solicitud_codigo>/', views_workflow.api_apc_detail, name='api_apc_detail'),
    path('api/apc/check-status/<int:solicitud_id>/', views_workflow.api_check_apc_status, name='api_check_apc_status'),
    
    # SURA Makito Tracking API URLs
    path('api/sura/list/', views_workflow.api_sura_list, name='api_sura_list'),
    path('api/sura/detail/<str:solicitud_codigo>/', views_workflow.api_sura_detail, name='api_sura_detail'),
    path('api/sura/check-status/<int:solicitud_id>/', views_workflow.api_check_sura_status, name='api_check_sura_status'),
    
    # Makito RPA API URLs for Debida Diligencia
    path('api/makito/debida-diligencia/update-status/<str:solicitud_codigo>/', views_workflow.api_makito_debida_diligencia_update_status, name='api_makito_debida_diligencia_update_status'),
    path('api/makito/debida-diligencia/upload/<str:solicitud_codigo>/', views_workflow.api_makito_debida_diligencia_upload, name='api_makito_debida_diligencia_upload'),
    
    # Debug URLs
    path('api/debug-session/', views_workflow.debug_session, name='debug_session'),
]
