from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .modelsWorkflow import RequisitoSolicitud
from .models import CalificacionDocumentoBackoffice, ComentarioDocumentoBackoffice, OpcionDesplegable
import json

@login_required
@require_http_methods(["POST"])
def calificar_documento(request):
    """Vista AJAX para calificar un documento"""
    try:
        data = json.loads(request.body)
        requisito_solicitud_id = data.get('requisito_solicitud_id')
        estado = data.get('estado')  # 'bueno' o 'malo'
        opcion_desplegable_id = data.get('opcion_desplegable_id')
        
        # Validar datos
        if not requisito_solicitud_id or estado not in ['bueno', 'malo', 'pendiente']:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_solicitud_id)
        
        # Obtener o crear calificación (un usuario solo puede tener una calificación por documento)
        calificacion, created = CalificacionDocumentoBackoffice.objects.update_or_create(
            requisito_solicitud=requisito_solicitud,
            calificado_por=request.user,
            defaults={
                'estado': estado,
                'opcion_desplegable_id': opcion_desplegable_id if opcion_desplegable_id else None
            }
        )
        
        # Preparar respuesta
        opcion_nombre = ""
        if calificacion.opcion_desplegable:
            opcion_nombre = calificacion.opcion_desplegable.nombre
        
        return JsonResponse({
            'success': True,
            'message': 'Calificación guardada exitosamente',
            'data': {
                'id': calificacion.id,
                'estado': calificacion.estado,
                'usuario': calificacion.calificado_por.username,
                'opcion': opcion_nombre,
                'fecha': calificacion.fecha_calificacion.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def comentar_documento(request):
    """Vista AJAX para agregar comentario a un documento"""
    try:
        data = json.loads(request.body)
        requisito_solicitud_id = data.get('requisito_solicitud_id')
        comentario_texto = data.get('comentario', '').strip()
        
        # Validar datos
        if not requisito_solicitud_id or not comentario_texto:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_solicitud_id)
        
        # Crear comentario
        comentario = ComentarioDocumentoBackoffice.objects.create(
            requisito_solicitud=requisito_solicitud,
            comentario_por=request.user,
            comentario=comentario_texto
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Comentario agregado exitosamente',
            'data': {
                'id': comentario.id,
                'comentario': comentario.comentario,
                'usuario': comentario.comentario_por.username,
                'fecha': comentario.fecha_comentario.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def editar_comentario(request):
    """Vista AJAX para editar un comentario existente (solo el autor puede editarlo)"""
    try:
        data = json.loads(request.body)
        comentario_id = data.get('comentario_id')
        nuevo_comentario = data.get('comentario', '').strip()
        
        # Validar datos
        if not comentario_id or not nuevo_comentario:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        
        comentario = get_object_or_404(ComentarioDocumentoBackoffice, id=comentario_id)
        
        # Solo el autor puede editar su comentario
        if comentario.comentario_por != request.user:
            return JsonResponse({'error': 'No tienes permisos para editar este comentario'}, status=403)
        
        comentario.comentario = nuevo_comentario
        comentario.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Comentario actualizado exitosamente',
            'data': {
                'id': comentario.id,
                'comentario': comentario.comentario,
                'fecha_modificacion': comentario.fecha_modificacion.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def obtener_comentarios_documento(request, requisito_solicitud_id):
    """Vista AJAX para obtener todos los comentarios de un documento"""
    try:
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_solicitud_id)
        
        comentarios = ComentarioDocumentoBackoffice.objects.filter(
            requisito_solicitud=requisito_solicitud,
            activo=True
        ).select_related('comentario_por').order_by('-fecha_comentario')
        
        comentarios_data = []
        for comentario in comentarios:
            # Obtener información del subestado donde se encuentra este requisito
            subestado_nombre = 'Sin subestado'
            try:
                # Obtener la solicitud y su etapa actual
                solicitud = requisito_solicitud.solicitud
                if solicitud.etapa_actual:
                    # Buscar el subestado actual de la solicitud
                    if solicitud.subestado_actual:
                        subestado_nombre = solicitud.subestado_actual.nombre
                    else:
                        # Si no hay subestado actual, intentar obtener el primer subestado de la etapa
                        primer_subestado = solicitud.etapa_actual.subestados.first()
                        if primer_subestado:
                            subestado_nombre = primer_subestado.nombre
            except Exception as e:
                print(f"Error obteniendo subestado: {e}")
                subestado_nombre = 'Sin subestado'
            
            comentarios_data.append({
                'id': comentario.id,
                'comentario': comentario.comentario,
                'usuario': comentario.comentario_por.username,
                'usuario_nombre': f"{comentario.comentario_por.first_name} {comentario.comentario_por.last_name}".strip() or comentario.comentario_por.username,
                'fecha': comentario.fecha_comentario.strftime('%d/%m/%Y %H:%M'),
                'puede_editar': comentario.comentario_por == request.user,
                'subestado': subestado_nombre,
                'etapa': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa'
            })
        
        return JsonResponse({
            'success': True,
            'data': comentarios_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def obtener_calificaciones_documento(request, requisito_solicitud_id):
    """Vista AJAX para obtener todas las calificaciones de un documento"""
    try:
        print(f"DEBUG: Solicitando calificaciones para requisito_solicitud_id: {requisito_solicitud_id}")
        
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_solicitud_id)
        print(f"DEBUG: RequisitoSolicitud encontrado: {requisito_solicitud}")
        
        calificaciones = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud=requisito_solicitud
        ).select_related('calificado_por', 'opcion_desplegable').order_by('-fecha_calificacion')
        
        print(f"DEBUG: Calificaciones encontradas: {calificaciones.count()}")
        
        calificaciones_data = []
        for calificacion in calificaciones:
            calificaciones_data.append({
                'id': calificacion.id,
                'estado': calificacion.estado,
                'usuario': calificacion.calificado_por.username,
                'usuario_nombre': f"{calificacion.calificado_por.first_name} {calificacion.calificado_por.last_name}".strip() or calificacion.calificado_por.username,
                'opcion': calificacion.opcion_desplegable.nombre if calificacion.opcion_desplegable else '',
                'fecha': calificacion.fecha_calificacion.strftime('%d/%m/%Y %H:%M'),
                'puede_editar': calificacion.calificado_por == request.user
            })
        
        print(f"DEBUG: Datos de respuesta preparados: {len(calificaciones_data)} items")
        
        return JsonResponse({
            'success': True,
            'data': calificaciones_data
        })
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        print(f"DEBUG ERROR TYPE: {type(e)}")
        import traceback
        print(f"DEBUG TRACEBACK: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
