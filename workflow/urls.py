from django.urls import path
from . import views
from . import api
from . import views_workflow
from . import views_negocios
from . import dashboard_views

from . import views_formulario
from . import views_comite
from . import apicomite
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
    path('agenda-firma/', views_workflow.agenda_firma_view, name='agenda_firma'),

    path('bandeja-trabajo/', views_workflow.bandeja_trabajo, name='bandeja_trabajo'),
    path('nueva-solicitud/', views_workflow.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:solicitud_id>/detalle/', views_workflow.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:solicitud_id>/backoffice/', views_workflow.detalle_solicitud, name='detalle_solicitud_backoffice'),
    
    # URLs específicas para cada subestado del Back Office
    path('solicitudes/<int:solicitud_id>/backoffice/checklist/', views_workflow.backoffice_checklist, name='backoffice_checklist'),
    path('solicitudes/<int:solicitud_id>/backoffice/captura/', views_workflow.backoffice_captura, name='backoffice_captura'),
    path('solicitudes/<int:solicitud_id>/backoffice/firma/', views_workflow.backoffice_firma, name='backoffice_firma'),
    path('solicitudes/<int:solicitud_id>/backoffice/orden/', views_workflow.backoffice_orden, name='backoffice_orden'),
    path('solicitudes/<int:solicitud_id>/backoffice/tramite/', views_workflow.backoffice_tramite, name='backoffice_tramite'),
    path('solicitudes/<int:solicitud_id>/backoffice/subsanacion/', views_workflow.backoffice_subsanacion, name='backoffice_subsanacion'),
    path('solicitudes/<int:solicitud_id>/transicion/', views_workflow.transicion_solicitud, name='transicion_solicitud'),
    path('solicitudes/<int:solicitud_id>/auto-asignar/', views_workflow.auto_asignar_solicitud, name='auto_asignar_solicitud'),
    path('solicitudes/<int:solicitud_id>/requisitos/<int:requisito_id>/actualizar/', views_workflow.actualizar_requisito, name='actualizar_requisito'),
    path('solicitudes/<int:solicitud_id>/campos-personalizados/', views_workflow.actualizar_campo_personalizado, name='actualizar_campo_personalizado'),
    
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
    path('api/solicitudes/<int:solicitud_id>/cambiar-subestado/', views_workflow.api_cambiar_subestado_backoffice, name='api_cambiar_subestado_backoffice'),
    
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
    
    # Comité View URLs (add these to resolve 404 error)
    path('comite/', views_comite.bandeja_comite_view, name='bandeja_comite'),
    path('comite/solicitud/<int:solicitud_id>/', views_comite.detalle_solicitud_comite, name='detalle_solicitud_comite'),
    
    # Additional Comité API URLs (from apicomite)
    path('api/comite/solicitudes/', apicomite.api_solicitudes_comite, name='api_solicitudes_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/participar/', apicomite.api_participar_comite, name='api_participar_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/escalar/', apicomite.api_escalar_comite, name='api_escalar_comite'),
    path('api/comite/niveles-usuario/', apicomite.api_niveles_usuario_comite, name='api_niveles_usuario_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/historial/', apicomite.api_historial_participaciones, name='api_historial_participaciones'),
    path('api/comite/solicitudes/<int:solicitud_id>/etapas-disponibles/', apicomite.api_etapas_disponibles_comite, name='api_etapas_disponibles_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/avanzar-etapa/', apicomite.api_avanzar_etapa_comite, name='api_avanzar_etapa_comite'),
    

    
    # URLs para asociación de entrevistas
    path('buscar-entrevistas/', views_workflow.buscar_entrevistas, name='buscar_entrevistas'),
    path('asociar-entrevista/', views_workflow.asociar_entrevista, name='asociar_entrevista'),
    
    # URLs para nuevo flujo de avance de subestado
    path('api/solicitudes/<int:solicitud_id>/siguiente-subestado/', views_workflow.api_obtener_siguiente_subestado, name='api_obtener_siguiente_subestado'),
    path('api/solicitudes/<int:solicitud_id>/validar-documentos/', views_workflow.api_validar_documentos_backoffice, name='api_validar_documentos_backoffice'),
    path('api/solicitudes/<int:solicitud_id>/avanzar-subestado/', views_workflow.api_avanzar_subestado_backoffice, name='api_avanzar_subestado_backoffice'),
    path('api/solicitudes/<int:solicitud_id>/transiciones-negativas/', views_workflow.api_obtener_transiciones_negativas, name='api_obtener_transiciones_negativas'),
    
    # Debug URLs
    path('api/debug-session/', views_workflow.debug_session, name='debug_session'),
    
    # APIs para Pendientes Antes de Firma
    path('api/pendientes/catalogo/', views_workflow.api_buscar_pendientes_catalogo, name='api_buscar_pendientes_catalogo'),
    path('api/solicitudes/<int:solicitud_id>/pendientes/', views_workflow.api_obtener_pendientes_solicitud, name='api_obtener_pendientes_solicitud'),
    path('api/solicitudes/<int:solicitud_id>/pendientes/agregar/', views_workflow.api_agregar_pendiente_solicitud, name='api_agregar_pendiente_solicitud'),
    path('api/pendientes/<int:pendiente_solicitud_id>/cambiar-estado/', views_workflow.api_cambiar_estado_pendiente, name='api_cambiar_estado_pendiente'),
    path('api/pendientes/<int:pendiente_solicitud_id>/eliminar/', views_workflow.api_eliminar_pendiente_solicitud, name='api_eliminar_pendiente_solicitud'),
    
    # APIs para Agenda de Firma
    path('api/agenda-firma/citas/', views_workflow.api_listar_citas_calendario, name='api_listar_citas_calendario'),
    path('api/agenda-firma/buscar-solicitudes/', views_workflow.api_buscar_solicitudes_agenda, name='api_buscar_solicitudes_agenda'),
    path('api/agenda-firma/crear-cita/', views_workflow.api_crear_cita_firma, name='api_crear_cita_firma'),
    path('api/agenda-firma/cita/<int:cita_id>/', views_workflow.api_obtener_cita_firma, name='api_obtener_cita_firma'),
    path('api/agenda-firma/solicitud/<int:solicitud_id>/', views_workflow.api_obtener_citas_solicitud, name='api_obtener_citas_solicitud'),
    path('api/agenda-firma/editar-cita/<int:cita_id>/', views_workflow.api_editar_cita_firma, name='api_editar_cita_firma'),
    path('api/agenda-firma/eliminar-cita/<int:cita_id>/', views_workflow.api_eliminar_cita_firma, name='api_eliminar_cita_firma'),
]
