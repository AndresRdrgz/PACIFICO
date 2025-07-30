from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
import json
import logging
from .modelsWorkflow import Solicitud, HistorialSolicitud


logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def api_sura_list(request):
    """
    API para listar todas las solicitudes con datos SURA
    """
    try:
        # Filtros opcionales
        status = request.GET.get('status')
        pipeline = request.GET.get('pipeline')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')

        # Base queryset - solo solicitudes con SURA habilitado
        queryset = Solicitud.objects.filter(cotizar_sura_makito=True).select_related(
            'pipeline',
            'etapa_actual',
            'cliente',
            'cotizacion',
            'asignada_a',
            'creada_por'
        ).order_by('-sura_fecha_solicitud', '-fecha_creacion')

        # Aplicar filtros
        if status:
            queryset = queryset.filter(sura_status=status)
        if pipeline:
            queryset = queryset.filter(pipeline_id=pipeline)
        if fecha_desde:
            queryset = queryset.filter(sura_fecha_solicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(sura_fecha_solicitud__lte=fecha_hasta)

        # Construir respuesta
        solicitudes_data = []
        for solicitud in queryset:
            # Preparar datos del cliente
            cliente_nombre = ""
            cliente_documento = ""
            
            if solicitud.cliente:
                cliente_nombre = solicitud.cliente.nombreCliente or ''
                cliente_documento = solicitud.cliente.cedulaCliente or ''
            elif solicitud.cotizacion and hasattr(solicitud.cotizacion, 'cliente_nombre'):
                cliente_nombre = solicitud.cotizacion.cliente_nombre or ''
                cliente_documento = solicitud.cotizacion.cliente_cedula or ''
            else:
                # Usar datos SURA directos
                cliente_nombre = f"{solicitud.sura_primer_nombre or ''} {solicitud.sura_segundo_nombre or ''} {solicitud.sura_primer_apellido or ''} {solicitud.sura_segundo_apellido or ''}".strip()
                cliente_documento = solicitud.sura_no_documento or ''

            solicitud_data = {
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'cliente_documento': cliente_documento,
                'pipeline': {
                    'id': solicitud.pipeline.id,
                    'nombre': solicitud.pipeline.nombre
                } if solicitud.pipeline else None,
                'etapa_actual': {
                    'id': solicitud.etapa_actual.id,
                    'nombre': solicitud.etapa_actual.nombre
                } if solicitud.etapa_actual else None,
                'asignada_a': {
                    'id': solicitud.asignada_a.id,
                    'username': solicitud.asignada_a.username,
                    'full_name': solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username
                } if solicitud.asignada_a else None,
                'creada_por': {
                    'id': solicitud.creada_por.id,
                    'username': solicitud.creada_por.username,
                    'full_name': solicitud.creada_por.get_full_name() or solicitud.creada_por.username
                } if solicitud.creada_por else None,
                
                # Datos específicos de SURA
                'sura_status': solicitud.sura_status,
                'sura_status_display': solicitud.get_sura_status_display(),
                'sura_fecha_solicitud': solicitud.sura_fecha_solicitud.isoformat() if solicitud.sura_fecha_solicitud else None,
                'sura_fecha_inicio': solicitud.sura_fecha_inicio.isoformat() if solicitud.sura_fecha_inicio else None,
                'sura_fecha_completado': solicitud.sura_fecha_completado.isoformat() if solicitud.sura_fecha_completado else None,
                'sura_observaciones': solicitud.sura_observaciones,
                'sura_archivo_url': solicitud.sura_archivo.url if solicitud.sura_archivo else None,
                'sura_archivo_name': solicitud.sura_archivo.name.split('/')[-1] if solicitud.sura_archivo else None,
                
                # Datos adicionales
                'fecha_creacion': solicitud.fecha_creacion.isoformat(),
                'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
            }
            solicitudes_data.append(solicitud_data)

        return JsonResponse({
            'success': True,
            'data': solicitudes_data,
            'total': len(solicitudes_data)
        })

    except Exception as e:
        logger.error(f"Error al obtener lista SURA: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_sura_detail(request, codigo):
    """
    API para obtener detalles específicos de una solicitud SURA
    """
    try:
        solicitud = get_object_or_404(Solicitud, codigo=codigo, cotizar_sura_makito=True)
        
        # Preparar datos detallados
        cliente_nombre = ""
        cliente_documento = ""
        cliente_datos = {}
        
        if solicitud.cliente:
            cliente_nombre = f"{solicitud.cliente.primer_nombre or ''} {solicitud.cliente.segundo_nombre or ''} {solicitud.cliente.primer_apellido or ''} {solicitud.cliente.segundo_apellido or ''}".strip()
            cliente_documento = solicitud.cliente.cedula or ''
            cliente_datos = {
                'primer_nombre': solicitud.cliente.primer_nombre,
                'segundo_nombre': solicitud.cliente.segundo_nombre,
                'primer_apellido': solicitud.cliente.primer_apellido,
                'segundo_apellido': solicitud.cliente.segundo_apellido,
                'cedula': solicitud.cliente.cedula,
                'telefono': getattr(solicitud.cliente, 'telefono', ''),
                'email': getattr(solicitud.cliente, 'email', ''),
            }
        elif solicitud.cotizacion:
            cliente_nombre = getattr(solicitud.cotizacion, 'cliente_nombre', '')
            cliente_documento = getattr(solicitud.cotizacion, 'cliente_cedula', '')

        # Timeline de eventos SURA
        timeline = []
        if solicitud.sura_fecha_solicitud:
            timeline.append({
                'fecha': solicitud.sura_fecha_solicitud.isoformat(),
                'evento': 'Solicitud SURA enviada',
                'estado': 'pending',
                'descripcion': 'Solicitud de cotización SURA enviada a Makito RPA'
            })
        
        if solicitud.sura_fecha_inicio:
            timeline.append({
                'fecha': solicitud.sura_fecha_inicio.isoformat(),
                'evento': 'Proceso iniciado',
                'estado': 'in_progress',
                'descripcion': 'Makito RPA ha comenzado el procesamiento'
            })
        
        if solicitud.sura_fecha_completado:
            timeline.append({
                'fecha': solicitud.sura_fecha_completado.isoformat(),
                'evento': 'Proceso completado',
                'estado': 'completed',
                'descripcion': 'Cotización SURA completada exitosamente'
            })

        # Ordenar timeline por fecha
        timeline.sort(key=lambda x: x['fecha'])

        response_data = {
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'cliente_nombre': cliente_nombre,
            'cliente_documento': cliente_documento,
            'cliente_datos': cliente_datos,
            'pipeline': {
                'id': solicitud.pipeline.id,
                'nombre': solicitud.pipeline.nombre
            } if solicitud.pipeline else None,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id,
                'nombre': solicitud.etapa_actual.nombre
            } if solicitud.etapa_actual else None,
            
            # Datos SURA específicos
            'sura_primer_nombre': solicitud.sura_primer_nombre,
            'sura_segundo_nombre': solicitud.sura_segundo_nombre,
            'sura_primer_apellido': solicitud.sura_primer_apellido,
            'sura_segundo_apellido': solicitud.sura_segundo_apellido,
            'sura_no_documento': solicitud.sura_no_documento,
            'sura_status': solicitud.sura_status,
            'sura_status_display': solicitud.get_sura_status_display(),
            'sura_fecha_solicitud': solicitud.sura_fecha_solicitud.isoformat() if solicitud.sura_fecha_solicitud else None,
            'sura_fecha_inicio': solicitud.sura_fecha_inicio.isoformat() if solicitud.sura_fecha_inicio else None,
            'sura_fecha_completado': solicitud.sura_fecha_completado.isoformat() if solicitud.sura_fecha_completado else None,
            'sura_observaciones': solicitud.sura_observaciones,
            'sura_archivo_url': solicitud.sura_archivo.url if solicitud.sura_archivo else None,
            'sura_archivo_name': solicitud.sura_archivo.name.split('/')[-1] if solicitud.sura_archivo else None,
            
            # Timeline y metadata
            'timeline': timeline,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
        }

        return JsonResponse({
            'success': True,
            'data': response_data
        })

    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f"Error al obtener detalle SURA {codigo}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_reenviar_sura_makito(request, codigo):
    """
    API para reenviar solicitud SURA a Makito RPA
    Solo disponible para superusuarios
    """
    # Verificar que el usuario sea superusuario
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para realizar esta acción'
        }, status=403)
    
    try:
        # Obtener la solicitud
        solicitud = get_object_or_404(Solicitud, codigo=codigo)
        
        # Verificar que la solicitud tenga datos SURA
        if not solicitud.cotizar_sura_makito:
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud no tiene cotización SURA habilitada'
            })
        
        if not solicitud.sura_no_documento:
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud no tiene número de documento SURA configurado'
            })
        
        # Importar la función de envío de correo
        from .views_workflow import enviar_correo_sura_makito
        
        # Enviar el correo SURA nuevamente
        enviar_correo_sura_makito(
            solicitud,
            solicitud.sura_primer_nombre,
            solicitud.sura_primer_apellido,
            solicitud.sura_no_documento,
            request
        )
        
        # Crear un registro en el historial
        try:
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now(),
                observaciones=f"Cotización SURA reenviada a Makito RPA por {request.user.get_full_name() or request.user.username}"
            )
        except Exception as hist_error:
            # Si falla el historial, no rompemos el flujo
            logger.warning(f"Error al crear historial de reenvío SURA: {hist_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud SURA {codigo} reenviada exitosamente a Makito RPA',
            'timestamp': timezone.now().isoformat()
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f"Error al reenviar SURA para solicitud {codigo}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


# ==========================================
# APIs PARA MAKITO RPA - WEBHOOKS
# ==========================================

@csrf_exempt
@require_http_methods(["POST"])
def api_sura_webhook_status(request, codigo):
    """
    Webhook para que Makito RPA actualice el estado de las solicitudes SURA
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        status = data.get('status')
        
        if not status:
            return JsonResponse({
                'success': False,
                'error': 'Estado requerido'
            }, status=400)
        
        # Validar que el status sea válido
        valid_statuses = ['pending', 'in_progress', 'completed', 'error']
        if status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'error': f'Estado inválido. Debe ser uno de: {", ".join(valid_statuses)}'
            }, status=400)
        
        # Buscar la solicitud
        try:
            solicitud = Solicitud.objects.get(codigo=codigo, cotizar_sura_makito=True)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Solicitud SURA {codigo} no encontrada'
            }, status=404)
        
        # Actualizar el estado
        with transaction.atomic():
            old_status = solicitud.sura_status
            solicitud.sura_status = status
            
            # Actualizar fechas según el estado
            now = timezone.now()
            if status == 'in_progress' and not solicitud.sura_fecha_inicio:
                solicitud.sura_fecha_inicio = now
            elif status == 'completed' and not solicitud.sura_fecha_completado:
                solicitud.sura_fecha_completado = now
            
            # Actualizar observaciones si se proporcionan
            observaciones = data.get('observaciones', '')
            if observaciones:
                if solicitud.sura_observaciones:
                    solicitud.sura_observaciones += f"\n{now.strftime('%Y-%m-%d %H:%M:%S')}: {observaciones}"
                else:
                    solicitud.sura_observaciones = f"{now.strftime('%Y-%m-%d %H:%M:%S')}: {observaciones}"
            
            solicitud.save()
            
            # Crear entrada en el historial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                fecha_inicio=now
            )
        
        logger.info(f"Estado SURA actualizado para solicitud {codigo}: {old_status} -> {status}")
        
        return JsonResponse({
            'success': True,
            'message': f'Estado SURA actualizado exitosamente para solicitud {codigo}',
            'old_status': old_status,
            'new_status': status,
            'timestamp': now.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Error en webhook SURA status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_sura_webhook_upload(request, codigo):
    """
    Webhook para que Makito RPA suba el archivo de cotización SURA
    """
    try:
        # Validar que se haya enviado un archivo
        if 'sura_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Archivo requerido (campo: sura_file)'
            }, status=400)
        
        # Buscar la solicitud
        try:
            solicitud = Solicitud.objects.get(codigo=codigo, cotizar_sura_makito=True)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Solicitud SURA {codigo} no encontrada'
            }, status=404)
        
        # Procesar el archivo
        uploaded_file = request.FILES['sura_file']
        
        # Validar tipo de archivo (opcional)
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
        file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Tipo de archivo no permitido. Tipos permitidos: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # Guardar el archivo
        with transaction.atomic():
            # Eliminar archivo anterior si existe
            if solicitud.sura_archivo:
                try:
                    default_storage.delete(solicitud.sura_archivo.name)
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo SURA anterior: {e}")
            
            # Guardar nuevo archivo
            file_name = f"sura_{codigo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            solicitud.sura_archivo.save(file_name, uploaded_file)
            
            # Actualizar estado si no está completado
            if solicitud.sura_status != 'completed':
                solicitud.sura_status = 'completed'
                if not solicitud.sura_fecha_completado:
                    solicitud.sura_fecha_completado = timezone.now()
            
            solicitud.save()
            
            # Crear entrada en el historial
            now = timezone.now()
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                fecha_inicio=now
            )
        
        logger.info(f"Archivo SURA subido para solicitud {codigo}: {file_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'Archivo SURA subido exitosamente para solicitud {codigo}',
            'file_name': file_name,
            'file_url': solicitud.sura_archivo.url,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en webhook SURA upload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)
