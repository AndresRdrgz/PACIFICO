from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import ClienteEntrevista
from .modelsWorkflow import Solicitud, CalificacionCampo
import json

def entrevistas_json(request):
    entrevistas = ClienteEntrevista.objects.all()
    data = []
    for entrevista in entrevistas:
        # Excluye lugar_nacimiento y asegura nacionalidad
        registro = {field.name: getattr(entrevista, field.name) for field in ClienteEntrevista._meta.fields if field.name != 'lugar_nacimiento'}
        if 'nacionalidad' not in registro:
            registro['nacionalidad'] = getattr(entrevista, 'nacionalidad', None)
        # Relacionados: Otros Ingresos
        registro['otros_ingresos'] = [
            {
                'tipo_ingreso': oi.tipo_ingreso,
                'fuente': oi.fuente,
                'monto': float(oi.monto) if oi.monto is not None else None
            }
            for oi in entrevista.otros_ingresos.all()
        ]
        # Relacionados: Referencias Personales
        registro['referencias_personales'] = [
            {
                'nombre': rp.nombre,
                'telefono': rp.telefono,
                'relacion': rp.relacion,
                'direccion': rp.direccion
            }
            for rp in entrevista.referencias_personales.all()
        ]
        # Relacionados: Referencias Comerciales
        registro['referencias_comerciales'] = [
            {
                'tipo': rc.tipo,
                'nombre': rc.nombre,
                'actividad': rc.actividad,
                'telefono': rc.telefono,
                'celular': rc.celular,
                'saldo': float(rc.saldo) if rc.saldo is not None else None
            }
            for rc in entrevista.referencias_comerciales.all()
        ]
        # Conversión explícita para decimales (peso, estatura)
        if 'peso' in registro and registro['peso'] is not None:
            registro['peso'] = float(registro['peso'])
        if 'estatura' in registro and registro['estatura'] is not None:
            registro['estatura'] = float(registro['estatura'])

        data.append(registro)
    response = {
        "status": "success",
        "total": len(data),
        "data": data
    }
    return JsonResponse(response, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})


# ==========================================
# APIs PARA CALIFICACIONES DE COMPLIANCE
# ==========================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_calificar_campo(request, solicitud_id):
    """
    API para calificar un campo como bueno o malo
    """
    try:
        # Obtener solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Parsear datos JSON
        data = json.loads(request.body)
        campo = data.get('campo')
        estado = data.get('estado')
        
        # Validar datos
        if not campo or not estado:
            return JsonResponse({
                'success': False,
                'error': 'Campo y estado son requeridos'
            })
        
        if estado not in ['bueno', 'malo']:
            return JsonResponse({
                'success': False,
                'error': 'Estado debe ser "bueno" o "malo"'
            })
        
        # Crear o actualizar calificación
        with transaction.atomic():
            calificacion, created = CalificacionCampo.objects.get_or_create(
                solicitud=solicitud,
                campo=campo,
                defaults={
                    'estado': estado,
                    'usuario': request.user
                }
            )
            
            if not created:
                calificacion.estado = estado
                calificacion.usuario = request.user
                calificacion.save()
        
        return JsonResponse({
            'success': True,
            'calificacion': {
                'campo': calificacion.campo,
                'estado': calificacion.estado,
                'usuario': calificacion.usuario.username,
                'fecha_modificacion': calificacion.fecha_modificacion.isoformat()
            }
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_comentario_compliance(request, solicitud_id):
    """
    API para agregar/actualizar comentario de compliance
    """
    try:
        # Obtener solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Parsear datos JSON
        data = json.loads(request.body)
        campo = data.get('campo')
        comentario = data.get('comentario', '').strip()
        
        # Validar datos
        if not campo:
            return JsonResponse({
                'success': False,
                'error': 'Campo es requerido'
            })
        
        if not comentario:
            return JsonResponse({
                'success': False,
                'error': 'Comentario es requerido'
            })
        
        # Crear o actualizar calificación con comentario
        with transaction.atomic():
            calificacion, created = CalificacionCampo.objects.get_or_create(
                solicitud=solicitud,
                campo=campo,
                defaults={
                    'estado': 'sin_calificar',
                    'comentario': comentario,
                    'usuario': request.user
                }
            )
            
            if not created:
                calificacion.comentario = comentario
                calificacion.usuario = request.user
                calificacion.save()
        
        return JsonResponse({
            'success': True,
            'calificacion': {
                'campo': calificacion.campo,
                'estado': calificacion.estado,
                'comentario': calificacion.comentario,
                'usuario': calificacion.usuario.username,
                'fecha_modificacion': calificacion.fecha_modificacion.isoformat()
            }
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def api_obtener_calificaciones(request, solicitud_id):
    """
    API para obtener todas las calificaciones de una solicitud
    """
    try:
        # Obtener solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Obtener calificaciones
        calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud)
        
        # Formatear respuesta
        data = []
        for calificacion in calificaciones:
            data.append({
                'campo': calificacion.campo,
                'estado': calificacion.estado,
                'comentario': calificacion.comentario,
                'usuario': calificacion.usuario.username,
                'fecha_modificacion': calificacion.fecha_modificacion.isoformat(),
                'estado_color': calificacion.get_estado_display_color(),
                'estado_icon': calificacion.get_estado_icon()
            })
        
        return JsonResponse({
            'success': True,
            'calificaciones': data
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })


# ==========================================
# APIs PARA COMENTARIOS DE ANALISTA DE CRÉDITO
# ==========================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_comentario_analista_credito(request, solicitud_id):
    """
    API para crear comentarios de analista de crédito con trazabilidad completa
    """
    try:
        # Obtener solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Parsear datos JSON
        data = json.loads(request.body)
        comentario_texto = data.get('comentario', '').strip()
        
        # Validar datos
        if not comentario_texto:
            return JsonResponse({
                'success': False,
                'error': 'Comentario es requerido'
            })
        
        if len(comentario_texto) > 2000:
            return JsonResponse({
                'success': False,
                'error': 'Comentario no puede exceder 2000 caracteres'
            })
        
        # Crear nuevo comentario usando CalificacionCampo con campo especial
        # Usar un identificador único que incluya timestamp para permitir múltiples comentarios
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        campo_comentario = f"comentario_analista_credito_{timestamp}"
        
        with transaction.atomic():
            calificacion = CalificacionCampo.objects.create(
                solicitud=solicitud,
                campo=campo_comentario,
                estado='sin_calificar',  # No aplicable para comentarios
                comentario=comentario_texto,
                usuario=request.user
            )
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': calificacion.id,
                'comentario': calificacion.comentario,
                'usuario_nombre': calificacion.usuario.get_full_name() or calificacion.usuario.username,
                'fecha_creacion': calificacion.fecha_creacion.isoformat(),
                'fecha_modificacion': calificacion.fecha_modificacion.isoformat()
            }
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def api_obtener_comentarios_analista_credito(request, solicitud_id):
    """
    API para obtener todos los comentarios de analista de crédito de una solicitud
    """
    try:
        # Obtener solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Obtener comentarios de analista (filtrar por campo que comience con "comentario_analista_credito_")
        comentarios = CalificacionCampo.objects.filter(
            solicitud=solicitud,
            campo__startswith='comentario_analista_credito_'
        ).order_by('fecha_creacion')
        
        # Formatear respuesta
        data = []
        for comentario in comentarios:
            data.append({
                'id': comentario.id,
                'comentario': comentario.comentario,
                'usuario_nombre': comentario.usuario.get_full_name() or comentario.usuario.username,
                'usuario_username': comentario.usuario.username,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'comentarios': data
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })
