from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from workflow.modelsWorkflow import Solicitud, HistorialSolicitud, TransicionEtapa, RequisitoSolicitud
from workflow.models import CalificacionDocumentoBackoffice
from .views_workflow import usuario_puede_modificar_solicitud


@login_required
def api_obtener_documentos_pendientes_backoffice_simple(request, solicitud_id):
    """API que copia EXACTAMENTE la lógica de detalle_solicitud para el checklist"""
    
    try:
        print(f"🔍 DEBUG MODAL CHECKLIST: Iniciando para solicitud {solicitud_id}")
        print(f"🔍 DEBUG MODAL CHECKLIST: Usuario: {request.user.username if request.user.is_authenticated else 'No autenticado'}")
        
        # Verificar que la solicitud existe
        try:
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            print(f"✅ DEBUG MODAL CHECKLIST: Solicitud encontrada: {solicitud.codigo}")
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error obteniendo solicitud: {str(e)}")
            return JsonResponse({'error': f'Solicitud no encontrada: {str(e)}'}, status=404)
        
        # Verificar etapa actual con manejo seguro
        try:
            etapa_nombre = solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa'
            es_bandeja_grupal = solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
            print(f"✅ DEBUG MODAL CHECKLIST: Etapa actual: {etapa_nombre}")
            print(f"✅ DEBUG MODAL CHECKLIST: Es bandeja grupal: {es_bandeja_grupal}")
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error verificando etapa: {str(e)}")
            etapa_nombre = 'Error'
            es_bandeja_grupal = False
        
        # Verificar permisos
        try:
            if not usuario_puede_modificar_solicitud(request.user, solicitud):
                print(f"❌ DEBUG MODAL CHECKLIST: Sin permisos para usuario {request.user.username}")
                return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error verificando permisos: {str(e)}")
            return JsonResponse({'error': f'Error verificando permisos: {str(e)}'}, status=500)
        
        # Verificar que esté en Back Office (con manejo más flexible)
        if not (solicitud.etapa_actual and etapa_nombre == "Back Office" and es_bandeja_grupal):
            print(f"❌ DEBUG MODAL CHECKLIST: No está en Back Office")
            print(f"❌ DEBUG MODAL CHECKLIST: etapa_actual: {solicitud.etapa_actual}")
            print(f"❌ DEBUG MODAL CHECKLIST: nombre: {etapa_nombre}")
            print(f"❌ DEBUG MODAL CHECKLIST: es_bandeja_grupal: {es_bandeja_grupal}")
            return JsonResponse({'error': 'Esta funcionalidad solo está disponible para solicitudes en Back Office'}, status=400)
        
        # ✅ COPIAR EXACTAMENTE LA LÓGICA DE detalle_solicitud (líneas 702-722)
        print(f"🔍 DEBUG MODAL CHECKLIST: Copiando lógica de detalle_solicitud...")
        
        # Obtener transiciones con manejo de errores
        try:
            transiciones_entrada = TransicionEtapa.objects.filter(
                pipeline=solicitud.pipeline,
                etapa_destino=solicitud.etapa_actual
            ).prefetch_related('requisitos_obligatorios__requisito')
            print(f"🔍 DEBUG MODAL CHECKLIST: {transiciones_entrada.count()} transiciones de entrada encontradas")
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error obteniendo transiciones: {str(e)}")
            return JsonResponse({'error': f'Error obteniendo transiciones: {str(e)}'}, status=500)
        
        # Obtener todos los requisitos necesarios (solo de entrada) - COPIA EXACTA
        requisitos_necesarios = {}
        
        try:
            # Procesar requisitos de transiciones de entrada - COPIA EXACTA
            for transicion in transiciones_entrada:
                try:
                    for req_transicion in transicion.requisitos_obligatorios.all():
                        # ✅ FILTRAR POR TIPO DE PRÉSTAMO usando el método del modelo
                        if solicitud.cotizacion and hasattr(solicitud.cotizacion, 'tipoPrestamo'):
                            if not req_transicion.aplica_para_cotizacion(solicitud.cotizacion):
                                continue  # Saltar este requisito si no aplica para este tipo de préstamo
                        
                        req_id = req_transicion.requisito.id
                        if req_id not in requisitos_necesarios:
                            requisitos_necesarios[req_id] = {
                                'requisito': req_transicion.requisito,
                                'obligatorio': req_transicion.obligatorio,
                                'mensaje_personalizado': req_transicion.mensaje_personalizado,
                                'archivo_actual': None,
                                'esta_cumplido': False,
                                'tipo_transicion': 'entrada'
                            }
                except Exception as e:
                    print(f"❌ DEBUG MODAL CHECKLIST: Error procesando transición {transicion.id}: {str(e)}")
                    continue
            
            print(f"🔍 DEBUG MODAL CHECKLIST: {len(requisitos_necesarios)} requisitos necesarios encontrados")
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error procesando requisitos: {str(e)}")
            return JsonResponse({'error': f'Error procesando requisitos: {str(e)}'}, status=500)
        
        # ✅ COPIAR EXACTAMENTE LA LÓGICA DE detalle_solicitud (líneas 725-739)
        # Verificar qué archivos ya están subidos (usar RequisitoSolicitud) - COPIA EXACTA
        try:
            requisitos_solicitud = RequisitoSolicitud.objects.filter(solicitud=solicitud).select_related('requisito')
            print(f"🔍 DEBUG MODAL CHECKLIST: {requisitos_solicitud.count()} RequisitoSolicitud encontrados")
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error obteniendo RequisitoSolicitud: {str(e)}")
            return JsonResponse({'error': f'Error obteniendo documentos: {str(e)}'}, status=500)
        
        documentos = []
        
        try:
            for req_sol in requisitos_solicitud:
                try:
                    req_id = req_sol.requisito_id  # Usar el foreign key directamente - IGUAL QUE ORIGINAL
                    print(f"🔍 DEBUG MODAL CHECKLIST: Procesando req_sol {req_sol.id} - requisito {req_id}")
                    
                    if req_id in requisitos_necesarios:
                        print(f"✅ DEBUG MODAL CHECKLIST: req_sol {req_sol.id} está en requisitos_necesarios")
                    else:
                        print(f"❌ DEBUG MODAL CHECKLIST: req_sol {req_sol.id} NO está en requisitos_necesarios - saltando")
                        continue
                        
                    # Obtener calificaciones y comentarios - COPIA EXACTA
                    try:
                        from .models import ComentarioDocumentoBackoffice, OpcionDesplegable
                        
                        calificaciones = CalificacionDocumentoBackoffice.objects.filter(
                            requisito_solicitud=req_sol
                        ).select_related('calificado_por', 'opcion_desplegable').order_by('-fecha_calificacion')
                        
                        comentarios = ComentarioDocumentoBackoffice.objects.filter(
                            requisito_solicitud=req_sol,
                            activo=True
                        ).select_related('comentario_por').order_by('-fecha_comentario')
                    except Exception as e:
                        print(f"❌ DEBUG MODAL CHECKLIST: Error obteniendo calificaciones para req_sol {req_sol.id}: {str(e)}")
                        # Continuar con valores por defecto
                        calificaciones = CalificacionDocumentoBackoffice.objects.none()
                        comentarios = []
                    
                    # Obtener información del requisito
                    req_info = requisitos_necesarios[req_id]
                    
                    # Determinar estado actual
                    try:
                        calificacion_actual = calificaciones.first() if calificaciones.exists() else None
                        if calificacion_actual:
                            # Si está marcado como subsanado, mostrar 'subsanado' en lugar del estado original
                            if calificacion_actual.subsanado:
                                estado_calificacion = 'subsanado'
                            else:
                                estado_calificacion = calificacion_actual.estado
                        else:
                            estado_calificacion = 'sin_calificar'
                    except Exception as e:
                        print(f"❌ DEBUG MODAL CHECKLIST: Error determinando estado para req_sol {req_sol.id}: {str(e)}")
                        calificacion_actual = None
                        estado_calificacion = 'sin_calificar'
                    
                    # MOSTRAR TODOS LOS DOCUMENTOS como en checklist (no filtrar por estado)
                    # El modal debe permitir calificar todos los documentos
                    try:
                        # Determinar si tiene archivo
                        tiene_archivo = bool(req_sol.archivo)
                        archivos_count = 1 if tiene_archivo else 0
                        
                        documento = {
                            'requisito_solicitud_id': req_sol.id,
                            'requisito_id': req_sol.requisito.id,
                            'nombre': req_sol.requisito.nombre,
                            'descripcion': req_sol.requisito.descripcion or 'Sin descripción disponible',
                            'obligatorio': req_info['obligatorio'],
                            'tiene_archivo': tiene_archivo,
                            'archivos_count': archivos_count,
                            'archivo_url': req_sol.archivo.url if tiene_archivo else None,
                            'archivo_nombre': req_sol.archivo.name.split('/')[-1] if tiene_archivo else None,
                            'estado_calificacion': estado_calificacion,
                            'fecha_calificacion': calificacion_actual.fecha_calificacion.isoformat() if calificacion_actual and calificacion_actual.fecha_calificacion else None,
                            'calificado_por': calificacion_actual.calificado_por.get_full_name() or calificacion_actual.calificado_por.username if calificacion_actual else None,
                            'observaciones': '',  # CalificacionDocumentoBackoffice no tiene campo observaciones
                            'cumplido': req_sol.cumplido,
                            'mensaje_personalizado': req_info['mensaje_personalizado'],
                            # Lógica de botones (misma que checklist + subsanado)
                            'puede_calificar_bueno': tiene_archivo,
                            'puede_calificar_malo': tiene_archivo,
                            'puede_calificar_pendiente': not req_info['obligatorio'],  # Solo opcionales
                            'puede_calificar_subsanado': True  # Siempre disponible
                        }
                        documentos.append(documento)
                        print(f"✅ DEBUG MODAL CHECKLIST: Documento agregado: {req_sol.requisito.nombre}")
                    except Exception as e:
                        print(f"❌ DEBUG MODAL CHECKLIST: Error creando documento para req_sol {req_sol.id}: {str(e)}")
                        continue
                except Exception as e:
                    print(f"❌ DEBUG MODAL CHECKLIST: Error procesando req_sol {req_sol.id if hasattr(req_sol, 'id') else 'unknown'}: {str(e)}")
                    continue
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error general procesando documentos: {str(e)}")
            return JsonResponse({'error': f'Error procesando documentos: {str(e)}'}, status=500)
                
        print(f"📊 DEBUG MODAL CHECKLIST: {len(documentos)} documentos a mostrar (TODOS los documentos como checklist)")
        
        # Verificar si ya se marcó como "Solicitud Completa"
        # HistorialSolicitud no tiene campo comentarios, usar otro método
        try:
            # Buscar en historial si hay alguna entrada que indique completitud
            # Como no hay campo comentarios, simplificar a False por ahora
            solicitud_completa = False
            print(f"🔍 DEBUG MODAL CHECKLIST: Solicitud completa: {solicitud_completa} (sin verificación de comentarios)")
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error verificando solicitud completa: {str(e)}")
            solicitud_completa = False
        
        try:
            response_data = {
                'success': True,
                'solicitud_id': solicitud.id,
                'solicitud_codigo': solicitud.codigo,
                'documentos': documentos,
                'total_documentos': len(documentos),
                'solicitud_completa': solicitud_completa,
                'mensaje_debug': 'Modal checklist - lógica copiada de detalle_solicitud con manejo de errores mejorado'
            }
            print(f"✅ DEBUG MODAL CHECKLIST: Respuesta exitosa con {len(documentos)} documentos")
            return JsonResponse(response_data)
        except Exception as e:
            print(f"❌ DEBUG MODAL CHECKLIST: Error creando respuesta: {str(e)}")
            return JsonResponse({'error': f'Error creando respuesta: {str(e)}'}, status=500)
        
    except Exception as e:
        print(f"❌ DEBUG MODAL CHECKLIST: Error: {str(e)}")
        import traceback
        print(f"❌ DEBUG MODAL CHECKLIST: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Error en modal checklist: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
def api_calificar_documento_modal(request, requisito_solicitud_id):
    """API para calificar documentos desde el modal (igual que checklist)"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        print(f"🔍 DEBUG CALIFICAR MODAL: Iniciando para requisito_solicitud {requisito_solicitud_id}")
        
        # CalificacionDocumentoBackoffice ya está importado arriba
        
        # Obtener datos del request
        data = json.loads(request.body)
        estado = data.get('estado')  # 'bueno', 'malo', 'pendiente', 'subsanado'
        observaciones = data.get('observaciones', '')  # No se usa pero se mantiene por compatibilidad
        
        if estado not in ['bueno', 'malo', 'pendiente', 'subsanado']:
            return JsonResponse({'error': 'Estado de calificación inválido'}, status=400)
        
        # Obtener RequisitoSolicitud
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_solicitud_id)
        solicitud = requisito_solicitud.solicitud
        
        print(f"✅ DEBUG CALIFICAR MODAL: RequisitoSolicitud encontrado: {requisito_solicitud.requisito.nombre}")
        
        # Verificar permisos
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            return JsonResponse({'error': 'No tienes permisos para calificar esta solicitud'}, status=403)
        
        # Verificar que esté en Back Office
        if not solicitud.etapa_actual or solicitud.etapa_actual.nombre != "Back Office":
            return JsonResponse({'error': 'Solo se puede calificar en Back Office'}, status=400)
        
        # Aplicar misma lógica que checklist: verificar si tiene archivo para bueno/malo
        tiene_archivo = bool(requisito_solicitud.archivo)
        
        if estado in ['bueno', 'malo'] and not tiene_archivo:
            return JsonResponse({
                'error': 'Debe subir un archivo antes de calificar como bueno o malo'
            }, status=400)
        
        # Subsanado se puede aplicar directamente sin validaciones previas
        
        # Crear o actualizar calificación (sin observaciones porque el modelo no lo tiene)
        calificacion, created = CalificacionDocumentoBackoffice.objects.get_or_create(
            requisito_solicitud=requisito_solicitud,
            defaults={
                'calificado_por': request.user,
                'estado': estado if estado != 'subsanado' else 'bueno',  # Si es subsanado directo, usar 'bueno' como base
                'fecha_calificacion': timezone.now(),
                'subsanado': estado == 'subsanado',
                'subsanado_por': request.user if estado == 'subsanado' else None,
                'fecha_subsanado': timezone.now() if estado == 'subsanado' else None
            }
        )
        
        if not created:
            # Actualizar calificación existente
            if estado == 'subsanado':
                # Para subsanado, si no hay estado previo o es sin_calificar, usar 'bueno' como base
                if not calificacion.estado or calificacion.estado == 'sin_calificar':
                    calificacion.estado = 'bueno'
                # Marcar como subsanado
                calificacion.subsanado = True
                calificacion.subsanado_por = request.user
                calificacion.fecha_subsanado = timezone.now()
                print(f"🔄 DEBUG SUBSANADO: Marcando como subsanado - estado: {calificacion.estado}, subsanado: {calificacion.subsanado}, por: {request.user}")
            else:
                # Para otros estados, actualizar normalmente y resetear subsanado
                calificacion.estado = estado
                calificacion.subsanado = False
                calificacion.subsanado_por = None
                calificacion.fecha_subsanado = None
                print(f"🔄 DEBUG ESTADO: Cambiando a estado: {estado}, reseteando subsanado")
            
            calificacion.calificado_por = request.user
            calificacion.fecha_calificacion = timezone.now()
            calificacion.save()
        
        print(f"✅ DEBUG CALIFICAR MODAL: Calificación {'creada' if created else 'actualizada'} como '{estado}'")
        
        # Si es "bueno" o "subsanado", marcar requisito como cumplido
        if estado in ['bueno', 'subsanado']:
            requisito_solicitud.cumplido = True
            requisito_solicitud.fecha_cumplimiento = timezone.now()
            requisito_solicitud.save()
            print(f"✅ DEBUG CALIFICAR MODAL: RequisitoSolicitud marcado como cumplido por '{estado}'")
        
        # Determinar si el documento debe desaparecer del modal
        # Los documentos calificos como "bueno" o "subsanado" desaparecen para que el usuario se enfoque en los pendientes
        desaparece_del_modal = estado in ['bueno', 'subsanado']
        
        return JsonResponse({
            'success': True,
            'message': f'Documento calificado como {estado}',
            'estado': estado,
            'calificacion_id': calificacion.id,
            'fecha_calificacion': calificacion.fecha_calificacion.isoformat(),
            'calificado_por': request.user.get_full_name() or request.user.username,
            'desaparece_del_modal': desaparece_del_modal
        })
        
    except Exception as e:
        print(f"❌ DEBUG CALIFICAR MODAL: Error: {str(e)}")
        import traceback
        print(f"❌ DEBUG CALIFICAR MODAL: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Error al calificar documento: {str(e)}'
        }, status=500)
