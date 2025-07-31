from django.urls import path
from django.views.static import serve
from django.conf import settings
from . import views_workflow
from . import views_negocios
from . import views
from . import api
from . import api_apc
from . import api_sura
from . import api_upload
from . import api_documentos
from . import views_comite
from . import apicomite
from . import dashboard_views
from . import views_reconsideraciones

# Import reportes views with error handling
try:
    from . import views_reportes
except ImportError as e:
    print(f"Error importing views_reportes: {e}")
    views_reportes = None

import os

app_name = 'workflow'

urlpatterns = [
    # Main routes
    ]

# Vistas principales
urlpatterns += [
    path('', views_workflow.dashboard_workflow, name='dashboard'),
    path('dashboard-operativo/', dashboard_views.dashboard_operativo, name='dashboard_operativo'),
    path('dashboard-usuario/', dashboard_views.dashboard_usuario, name='dashboard_usuario'),
    path('dashboard-cumplimiento/', dashboard_views.dashboard_cumplimiento, name='dashboard_cumplimiento'),
    path('dashboard-flujo/', dashboard_views.dashboard_flujo, name='dashboard_flujo'),
    path('dashboard-comite/', dashboard_views.dashboard_comite, name='dashboard_comite'),
    path('bandeja/', views_workflow.bandeja_trabajo, name='bandeja_trabajo'),
    path('bandeja-mixta/', views_workflow.vista_mixta_bandejas, name='vista_mixta_bandejas'),
    path('bandejas/', views_workflow.vista_mixta_bandejas, name='bandejas'),
    path('negocios/', views_negocios.negocios_view, name='negocios'),
    path('nueva-solicitud/', views_workflow.nueva_solicitud, name='nueva_solicitud'),
    path('solicitud/<int:solicitud_id>/v2/', views_workflow.detalle_solicitud_v2, name='detalle_solicitud_v2'),
    path('solicitud/<int:solicitud_id>/transicion/', views_workflow.transicion_solicitud, name='transicion_solicitud'),
    path('solicitud/<int:solicitud_id>/auto-asignar/', views_workflow.auto_asignar_solicitud, name='auto_asignar_solicitud'),
    path('solicitud/<int:solicitud_id>/requisito/<int:requisito_id>/actualizar/', views_workflow.actualizar_requisito, name='actualizar_requisito'),
    path('solicitud/<int:solicitud_id>/campos-personalizados/', views_workflow.actualizar_campo_personalizado, name='actualizar_campos_personalizados'),
    path('solicitud/<int:solicitud_id>/analisis/', views_workflow.detalle_solicitud_analisis, name='detalle_solicitud_analisis'),
    path('solicitud/<int:solicitud_id>/backoffice/', views_workflow.detalle_solicitud, name='detalle_solicitud_backoffice'),
    path('solicitud/<int:solicitud_id>/', views_workflow.detalle_solicitud, name='detalle_solicitud'),
    
    # Comité de Crédito URLs
    path('comite/', views_comite.bandeja_comite_view, name='bandeja_comite'),
    path('comite/solicitud/<int:solicitud_id>/', views_comite.detalle_solicitud_comite, name='detalle_solicitud_comite'),
    path('api/comite/solicitudes/', apicomite.api_solicitudes_comite, name='api_solicitudes_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/participar/', apicomite.api_participar_comite, name='api_participar_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/escalar/', apicomite.api_escalar_comite, name='api_escalar_comite'),
    path('api/comite/niveles-usuario/', apicomite.api_niveles_usuario_comite, name='api_niveles_usuario_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/historial/', apicomite.api_historial_participaciones, name='api_historial_participaciones'),
    path('api/comite/solicitudes/<int:solicitud_id>/etapas-disponibles/', apicomite.api_etapas_disponibles_comite, name='api_etapas_disponibles_comite'),
    path('api/comite/solicitudes/<int:solicitud_id>/avanzar-etapa/', apicomite.api_avanzar_etapa_comite, name='api_avanzar_etapa_comite'),
    
    # APIs para gestión de niveles de comité
    path('api/comite/niveles/', views_workflow.api_obtener_niveles_comite, name='api_obtener_niveles_comite'),
    path('api/comite/niveles/crear/', views_workflow.api_crear_nivel_comite, name='api_crear_nivel_comite'),
    path('api/comite/niveles/<int:nivel_id>/actualizar/', views_workflow.api_actualizar_nivel_comite, name='api_actualizar_nivel_comite'),
    path('api/comite/niveles/<int:nivel_id>/eliminar/', views_workflow.api_eliminar_nivel_comite, name='api_eliminar_nivel_comite'),
    
    # APIs para asignación de usuarios a niveles de comité
    path('api/comite/usuarios-disponibles/', views_workflow.api_obtener_usuarios_disponibles_comite, name='api_obtener_usuarios_disponibles_comite'),
    path('api/comite/asignar-usuario/', views_workflow.api_asignar_usuario_nivel_comite, name='api_asignar_usuario_nivel_comite'),
    path('api/comite/usuarios/<int:usuario_id>/niveles/<int:nivel_id>/desasignar/', views_workflow.api_desasignar_usuario_nivel_comite, name='api_desasignar_usuario_nivel_comite'),
    
    # APIs para bandeja mixta
    path('api/solicitudes/<int:solicitud_id>/tomar/', views_workflow.api_tomar_solicitud, name='api_tomar_solicitud'),
    path('api/solicitudes/<int:solicitud_id>/devolver/', views_workflow.api_devolver_solicitud, name='api_devolver_solicitud'),
    path('api/kpis/', views_workflow.api_kpis, name='api_kpis'),
    path('api/bandejas/', views_workflow.api_bandejas, name='api_bandejas'),
    path('api/notifications/stream/', views_workflow.api_notifications_stream, name='api_notifications_stream'),
    path('api/check-updates/', views_workflow.api_check_updates, name='api_check_updates'),
    path('api/get-updated-solicitudes/', views_workflow.api_get_updated_solicitudes, name='api_get_updated_solicitudes'),
    
    # API para solicitudes procesadas
    path('api/solicitudes-procesadas/', views_workflow.api_solicitudes_procesadas, name='api_solicitudes_procesadas'),
    
    # Comments API URLs
    path('api/solicitudes/<int:solicitud_id>/comentarios/', views_workflow.api_obtener_comentarios, name='api_obtener_comentarios'),
    path('api/solicitudes/<int:solicitud_id>/comentarios/crear/', views_workflow.api_crear_comentario, name='api_crear_comentario'),
    path('api/comentarios/<int:comentario_id>/editar/', views_workflow.api_editar_comentario, name='api_editar_comentario'),
    path('api/comentarios/<int:comentario_id>/eliminar/', views_workflow.api_eliminar_comentario, name='api_eliminar_comentario'),
    
    # Document Upload API URL
    path('api/upload-documento/', api_upload.api_upload_documento, name='api_upload_documento'),
    
    # Document List API URL
    path('api/solicitud/<int:solicitud_id>/documentos/', api_documentos.api_obtener_documentos_solicitud, name='api_obtener_documentos_solicitud'),
    
    # Reconsideraciones URLs
    path('solicitud/<int:solicitud_id>/reconsideracion/solicitar/', views_reconsideraciones.solicitar_reconsideracion, name='solicitar_reconsideracion'),
    path('solicitud/<int:solicitud_id>/reconsideracion/analista/', views_reconsideraciones.detalle_reconsideracion_analista, name='detalle_reconsideracion_analista'),
    path('solicitud/<int:solicitud_id>/reconsideracion/comite/', views_reconsideraciones.detalle_reconsideracion_comite, name='detalle_reconsideracion_comite'),
    
    # APIs para Reconsideraciones
    path('api/solicitud/<int:solicitud_id>/reconsideracion/procesar/', views_reconsideraciones.api_procesar_reconsideracion_analista, name='api_procesar_reconsideracion_analista'),
    path('api/solicitud/<int:solicitud_id>/reconsideracion/historial/', views_reconsideraciones.api_historial_reconsideraciones, name='api_historial_reconsideraciones'),
    path('api/solicitud/<int:solicitud_id>/cotizaciones/', views_reconsideraciones.api_cotizaciones_cliente, name='api_cotizaciones_cliente'),
    
    # Solicitud brief API
    path('api/solicitud_brief/<int:solicitud_id>/', views_workflow.api_solicitud_brief, name='api_solicitud_brief'),
    
    # APC Status Check API
    path('api/solicitud/<int:solicitud_id>/apc-status/', views_workflow.api_check_apc_status, name='api_check_apc_status'),
    
    # SURA Status Check API
    path('api/solicitud/<int:solicitud_id>/sura-status/', views_workflow.api_check_sura_status, name='api_check_sura_status'),
    
    # Vistas de administración
    path('admin/pipelines/', views_workflow.administrar_pipelines, name='admin_pipelines'),
    path('admin/requisitos/', views_workflow.administrar_requisitos, name='admin_requisitos'),
    path('admin/campos-personalizados/', views_workflow.administrar_campos_personalizados, name='admin_campos_personalizados'),
    path('admin/usuarios/', views_workflow.administrar_usuarios, name='admin_usuarios'),
    
    # Vistas de reportes (comentada para usar la nueva vista)
    # path('reportes/', views_workflow.reportes_workflow, name='reportes'),
    
    # Canales Alternos
    path('canal-digital/', views_workflow.canal_digital, name='canal_digital'),
    path('formulario-web/', views_workflow.formulario_web, name='formulario_web'),
    path('api/convertir-formulario/', views_workflow.convertir_formulario_a_solicitud, name='convertir_formulario_a_solicitud'),
    path('api/procesar-formularios-masivo/', views_workflow.procesar_formularios_masivo, name='procesar_formularios_masivo'),
    
    # APIs para Canal Digital
    path('api/canal-digital/pipelines/', views_workflow.api_obtener_pipelines_canal_digital, name='api_obtener_pipelines_canal_digital'),
    path('api/canal-digital/pipelines/<int:pipeline_id>/etapas/', views_workflow.api_obtener_etapas_pipeline, name='api_obtener_etapas_pipeline'),
    path('api/canal-digital/configuracion/', views_workflow.api_obtener_configuracion_canal_digital, name='api_obtener_configuracion_canal_digital'),
    path('api/canal-digital/configuracion/guardar/', views_workflow.api_guardar_configuracion_canal_digital, name='api_guardar_configuracion_canal_digital'),
    path('api/canal-digital/propietario/asignar/', views_workflow.api_asignar_propietario_formulario, name='api_asignar_propietario_formulario'),
    path('api/canal-digital/usuarios/agregar/', views_workflow.api_agregar_usuario_canal_digital, name='api_agregar_usuario_canal_digital'),
    path('api/canal-digital/usuarios/remover/', views_workflow.api_remover_usuario_canal_digital, name='api_remover_usuario_canal_digital'),
    
    # APIs
    path('api/solicitudes/', views_negocios.api_solicitudes, name='api_solicitudes'),
    path('api/solicitudes/<int:solicitud_id>/detalle/', views_workflow.api_solicitud_detalle, name='api_solicitud_detalle'),
    path('api/estadisticas/', views_negocios.api_estadisticas, name='api_estadisticas'),
    
    # APIs para gestión de pipeline guardado en sesión
    path('api/negocios/clear-saved-pipeline/', views_negocios.api_clear_saved_pipeline, name='api_clear_saved_pipeline'),
    path('api/negocios/get-saved-pipeline/', views_negocios.api_get_saved_pipeline, name='api_get_saved_pipeline'),
    
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
    path('api/transiciones/<int:transicion_id>/eliminar/', views_workflow.api_eliminar_transicion, name='api_eliminar_transicion'),
    path('api/transiciones/<int:transicion_id>/editar/', views_workflow.api_editar_transicion, name='api_editar_transicion'),
    path('api/requisitos-pipeline/<int:requisito_pipeline_id>/eliminar/', views_workflow.api_eliminar_requisito_pipeline, name='api_eliminar_requisito_pipeline'),
    path('api/requisitos-pipeline/<int:requisito_pipeline_id>/editar/', views_workflow.api_editar_requisito_pipeline, name='api_editar_requisito_pipeline'),
    path('api/campos-personalizados/<int:campo_id>/eliminar/', views_workflow.api_eliminar_campo_personalizado, name='api_eliminar_campo_personalizado'),
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
    
    # APIs específicas para el drawer
    path('api/buscar-clientes-drawer/', views_workflow.api_buscar_clientes_drawer, name='api_buscar_clientes_drawer'),
    path('api/buscar-cotizaciones-drawer/', views_workflow.api_buscar_cotizaciones_drawer, name='api_buscar_cotizaciones_drawer'),
    
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
    
    # API para obtener etapa con subestados
    path('api/etapas/<int:etapa_id>/subestados/', views_workflow.api_obtener_etapa_con_subestados, name='api_obtener_etapa_con_subestados'),
    
    # APIs para modal de requisitos faltantes
    path('api/solicitudes/<int:solicitud_id>/requisitos-faltantes-detallado/', views_workflow.api_obtener_requisitos_faltantes_detallado, name='api_obtener_requisitos_faltantes_detallado'),
    path('api/solicitudes/<int:solicitud_id>/subir-requisito-modal/', views_workflow.api_subir_requisito_modal, name='api_subir_requisito_modal'),
    
    # URLs de testing para correos (eliminar en producción)
    path('test-correo-bandeja/', views_workflow.test_envio_correo_bandeja, name='test_correo_bandeja'),
    path('test-correo-asignacion/', views_workflow.test_envio_correo_asignacion, name='test_correo_asignacion'),
    path('test-correo-cambio-etapa/', views_workflow.test_envio_correo_cambio_etapa, name='test_correo_cambio_etapa'),
    # APIs para gestión de permisos de pipeline
    path('api/pipelines/<int:pipeline_id>/permisos/', views_workflow.api_obtener_permisos_pipeline, name='api_obtener_permisos_pipeline'),
    path('api/pipelines/<int:pipeline_id>/permisos/crear/', views_workflow.api_crear_permiso_pipeline, name='api_crear_permiso_pipeline'),
    path('api/pipelines/<int:pipeline_id>/permisos/<int:permiso_id>/actualizar/', views_workflow.api_actualizar_permiso_pipeline, name='api_actualizar_permiso_pipeline'),
    path('api/pipelines/<int:pipeline_id>/permisos/<int:permiso_id>/eliminar/', views_workflow.api_eliminar_permiso_pipeline, name='api_eliminar_permiso_pipeline'),
    
    # APIs para gestión de permisos de bandeja
    path('api/etapas/<int:etapa_id>/permisos/', views_workflow.api_obtener_permisos_bandeja, name='api_obtener_permisos_bandeja'),
    path('api/etapas/<int:etapa_id>/permisos/crear/', views_workflow.api_crear_permiso_bandeja, name='api_crear_permiso_bandeja'),
    path('api/etapas/<int:etapa_id>/permisos/<int:permiso_id>/actualizar/', views_workflow.api_actualizar_permiso_bandeja, name='api_actualizar_permiso_bandeja'),
    path('api/etapas/<int:etapa_id>/permisos/<int:permiso_id>/eliminar/', views_workflow.api_eliminar_permiso_bandeja, name='api_eliminar_permiso_bandeja'),
    
    # APIs para obtener usuarios y grupos
    path('api/usuarios/', views_workflow.api_obtener_usuarios, name='api_obtener_usuarios'),
    path('api/grupos/', views_workflow.api_obtener_grupos, name='api_obtener_grupos'),
    
    # APIs para calificaciones de compliance
    path('api/solicitudes/<int:solicitud_id>/calificar-campo/', api.api_calificar_campo, name='api_calificar_campo'),
    path('api/solicitudes/<int:solicitud_id>/calificar-campos-bulk/', api.api_calificar_campos_bulk, name='api_calificar_campos_bulk'),
    path('api/solicitudes/<int:solicitud_id>/comentario-compliance/', api.api_comentario_compliance, name='api_comentario_compliance'),
    path('api/solicitudes/<int:solicitud_id>/calificaciones/', api.api_obtener_calificaciones, name='api_obtener_calificaciones'),
    
    # APIs para comentarios de analista de crédito
    path('api/solicitudes/<int:solicitud_id>/comentario-analista-credito/', api.api_comentario_analista_credito, name='api_comentario_analista_credito'),
    path('api/solicitudes/<int:solicitud_id>/comentarios-analista-credito/', api.api_obtener_comentarios_analista_credito, name='api_obtener_comentarios_analista_credito'),
    
    # API para PDF resultado consulta
    path('api/solicitudes/<int:solicitud_id>/pdf-resultado-consulta/', views_workflow.api_pdf_resultado_consulta, name='api_pdf_resultado_consulta'),
    
    # APIs para asignación de solicitudes
    path('api/solicitudes/<int:solicitud_id>/usuarios-disponibles/', api.api_usuarios_disponibles, name='api_usuarios_disponibles'),
    path('api/solicitudes/<int:solicitud_id>/asignar-usuario/', api.api_asignar_usuario, name='api_asignar_usuario'),
    
    # API para validación de cotización duplicada
    path('api/validate-cotizacion-duplicate/', api.api_validate_cotizacion_duplicate, name='api_validate_cotizacion_duplicate'),
    
    # Unified Makito Tracking URL
    path('makito-tracking/', views_workflow.makito_tracking_view, name='makito_tracking'),
    
    # APC Makito Tracking URLs (legacy)
    path('apc-tracking/', views_workflow.apc_tracking_view, name='apc_tracking'),
    path('api/apc/list/', views_workflow.api_apc_list, name='api_apc_list'),
    path('api/apc/detail/<str:solicitud_codigo>/', views_workflow.api_apc_detail, name='api_apc_detail'),
    path('api/apc/reenviar/<str:codigo>/', api_apc.api_reenviar_apc_makito, name='api_reenviar_apc_makito'),
    path('api/makito/update-status/<str:solicitud_codigo>/', views_workflow.api_makito_update_status, name='api_makito_update_status'),
    path('api/makito/upload-apc/<str:solicitud_codigo>/', views_workflow.api_makito_upload_apc, name='api_makito_upload_apc'),
    
    # SURA Makito URLs
    path('sura-tracking/', views_workflow.sura_tracking_view, name='sura_tracking'),
    path('api/sura/list/', api_sura.api_sura_list, name='api_sura_list'),
    path('api/sura/detail/<str:codigo>/', api_sura.api_sura_detail, name='api_sura_detail'),
    path('api/sura/reenviar/<str:codigo>/', api_sura.api_reenviar_sura_makito, name='api_reenviar_sura_makito'),
    
    # SURA Makito Webhooks for RPA
    path('api/sura/update-status/<str:codigo>/', api_sura.api_sura_webhook_status, name='api_sura_webhook_status'),
    path('api/sura/upload-file/<str:codigo>/', api_sura.api_sura_webhook_upload, name='api_sura_webhook_upload'),
    
    # Testing URLs (remove in production)
    path('test/apc-upload-email/', views_workflow.test_apc_upload_email, name='test_apc_upload_email'),
    path('test/apc-iniciado-email/', views_workflow.test_apc_iniciado_email, name='test_apc_iniciado_email'),
    path('test/sura-completado-email/', views_workflow.test_sura_completado_email, name='test_sura_completado_email'),
    path('test/sura-iniciado-email/', views_workflow.test_sura_iniciado_email, name='test_sura_iniciado_email'),
    path('test/sura-error-email/', views_workflow.test_sura_error_email, name='test_sura_error_email'),
]

# Add reportes URLs only if views_reportes imported successfully
if views_reportes is not None:
    urlpatterns += [
        # Reportes URLs
        path('reportes/', views_reportes.reportes_dashboard, name='reportes'),
        
        # Reportes API URLs
        path('reportes/api/crear/', views_reportes.api_crear_reporte, name='api_crear_reporte'),
        path('reportes/api/crear-prueba/', views_reportes.api_crear_reporte_prueba, name='api_crear_reporte_prueba'),
        path('reportes/api/obtener-usuario/', views_reportes.api_obtener_reportes_usuario, name='api_obtener_reportes_usuario'),
        path('reportes/api/<int:reporte_id>/ejecutar/', views_reportes.api_ejecutar_reporte, name='api_ejecutar_reporte'),
        path('reportes/api/<int:reporte_id>/exportar/', views_reportes.api_exportar_reporte, name='api_exportar_reporte'),
        path('reportes/api/<int:reporte_id>/eliminar/', views_reportes.api_eliminar_reporte, name='api_eliminar_reporte'),
        path('reportes/api/reportes-predefinidos/', views_reportes.api_reportes_predefinidos, name='api_reportes_predefinidos'),
    ]


