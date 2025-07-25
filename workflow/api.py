from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .models import ClienteEntrevista
from .modelsWorkflow import Solicitud, CalificacionCampo, HistorialSolicitud, PermisoEtapa
from .views_workflow import notify_solicitud_change
import json
import logging
import traceback

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
    import time
    from django.db import OperationalError
    
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
        
        # Crear o actualizar calificación con retry logic for database locks
        max_retries = 3
        retry_delay = 0.1  # 100ms
        
        for attempt in range(max_retries):
            try:
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
                
            except OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    # Wait before retrying
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
        
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
    except OperationalError as e:
        if "database is locked" in str(e).lower():
            return JsonResponse({
                'success': False,
                'error': 'Base de datos ocupada. Intente nuevamente en unos segundos.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
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
    import logging
    logger = logging.getLogger(__name__)
    
    print(f"=== api_comentario_compliance START ===")
    print(f"Request method: {request.method}")
    print(f"Solicitud ID: {solicitud_id}")
    print(f"User: {request.user.username}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        # Log request body
        print(f"Request body: {request.body}")
        
        # Obtener solicitud
        print(f"Looking for solicitud with ID: {solicitud_id}")
        solicitud = Solicitud.objects.get(id=solicitud_id)
        print(f"Solicitud found: {solicitud}")
        
        # Parsear datos JSON
        print(f"Parsing JSON from request body...")
        data = json.loads(request.body)
        print(f"Parsed data: {data}")
        
        campo = data.get('campo')
        comentario = data.get('comentario', '').strip()
        
        print(f"Extracted campo: {campo}")
        print(f"Extracted comentario: {comentario}")
        
        # Validar datos
        if not campo:
            print(f"ERROR: Campo is empty or None")
            return JsonResponse({
                'success': False,
                'error': 'Campo es requerido'
            })
        
        if not comentario:
            print(f"ERROR: Comentario is empty or None")
            return JsonResponse({
                'success': False,
                'error': 'Comentario es requerido'
            })
        
        print(f"Data validation passed. Proceeding with database operation...")
        
        # Crear o actualizar calificación con comentario
        with transaction.atomic():
            print(f"Starting database transaction...")
            
            calificacion, created = CalificacionCampo.objects.get_or_create(
                solicitud=solicitud,
                campo=campo,
                defaults={
                    'estado': 'sin_calificar',
                    'comentario': comentario,
                    'usuario': request.user
                }
            )
            
            print(f"Calificacion get_or_create result: created={created}, calificacion={calificacion}")
            
            if not created:
                print(f"Updating existing calificacion...")
                calificacion.comentario = comentario
                calificacion.usuario = request.user
                calificacion.save()
                print(f"Calificacion updated successfully")
            else:
                print(f"New calificacion created successfully")
        
        response_data = {
            'success': True,
            'calificacion': {
                'campo': calificacion.campo,
                'estado': calificacion.estado,
                'comentario': calificacion.comentario,
                'usuario': calificacion.usuario.username,
                'fecha_modificacion': calificacion.fecha_modificacion.isoformat()
            }
        }
        
        print(f"Returning success response: {response_data}")
        return JsonResponse(response_data)
        
    except Solicitud.DoesNotExist:
        print(f"ERROR: Solicitud with ID {solicitud_id} not found")
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        })
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON decode error: {e}")
        print(f"Request body that caused error: {request.body}")
        return JsonResponse({
            'success': False,
            'error': f'Datos JSON inválidos: {str(e)}'
        })
    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })
    finally:
        print(f"=== api_comentario_compliance END ===")


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
        ).order_by('-fecha_creacion')  # Ordenar por fecha descendente (más reciente primero)
        
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


@login_required
@require_http_methods(["GET"])
def api_usuarios_disponibles(request, solicitud_id):
    """Obtener usuarios disponibles para asignar una solicitud"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos - solo superusers y staff pueden asignar
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para asignar solicitudes'
            }, status=403)
        
        # Obtener usuarios que tienen acceso a la etapa actual
        usuarios_disponibles = []
        
        if solicitud.etapa_actual:
            # Buscar usuarios que tienen permisos para esta etapa
            permisos_etapa = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                puede_ver=True
            ).select_related('grupo')
            
            # Obtener grupos que tienen acceso
            grupos_con_acceso = [permiso.grupo for permiso in permisos_etapa]
            
            # Buscar usuarios que pertenecen a esos grupos O son superusuarios
            usuarios = User.objects.filter(
                (Q(groups__in=grupos_con_acceso) | Q(is_superuser=True)),
                is_active=True
            ).distinct()
            
            for usuario in usuarios:
                # Obtener grupos del usuario
                grupos_usuario = usuario.groups.all()
                
                # Obtener información del perfil del usuario
                try:
                    user_profile = usuario.userprofile
                    profile_picture_url = user_profile.profile_picture.url if user_profile.profile_picture else None
                except:
                    profile_picture_url = None
                
                usuarios_disponibles.append({
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'nombre_completo': usuario.get_full_name() or usuario.username,
                    'grupos': [grupo.name for grupo in grupos_usuario],
                    'is_staff': usuario.is_staff,
                    'is_superuser': usuario.is_superuser,
                    'profile_picture_url': profile_picture_url
                })
        
        return JsonResponse({
            'success': True,
            'usuarios': usuarios_disponibles
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_asignar_usuario(request, solicitud_id):
    """Asignar una solicitud a un usuario específico"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos - solo superusers y staff pueden asignar
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para asignar solicitudes'
            }, status=403)
        
        # Obtener datos del request
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        
        if not usuario_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de usuario requerido'
            }, status=400)
        
        # Obtener el usuario
        try:
            usuario = User.objects.get(id=usuario_id, is_active=True)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Usuario no encontrado o inactivo'
            }, status=404)
        
        # Verificar que el usuario tiene acceso a la etapa
        if solicitud.etapa_actual:
            # Los superusuarios siempre tienen acceso
            if usuario.is_superuser:
                permisos_usuario = True
            else:
                # Verificar permisos de grupo para usuarios normales
                permisos_usuario = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=usuario.groups.all(),
                    puede_ver=True
                ).exists()
            
            if not permisos_usuario:
                return JsonResponse({
                    'success': False,
                    'error': 'El usuario no tiene permisos para esta etapa'
                }, status=403)
        
        # Asignar la solicitud al usuario
        solicitud.asignada_a = usuario
        solicitud.save()
        
        # Crear historial de la asignación
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            usuario_responsable=usuario,
            fecha_inicio=timezone.now()
        )
        
        # Notificar al usuario asignado
        notify_solicitud_change(solicitud, 'asignada', usuario)
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud asignada exitosamente a {usuario.get_full_name()}',
            'usuario_asignado': {
                'id': usuario.id,
                'nombre': usuario.get_full_name(),
                'email': usuario.email
            }
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_calificar_campos_bulk(request, solicitud_id):
    """
    API para calificar múltiples campos como buenos de una vez
    """
    import time
    from django.db import OperationalError
    
    try:
        # Obtener solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Parsear datos JSON
        data = json.loads(request.body)
        campos = data.get('campos', [])
        estado = data.get('estado', 'bueno')
        
        # Validar datos
        if not campos or not isinstance(campos, list):
            return JsonResponse({
                'success': False,
                'error': 'Lista de campos es requerida'
            })
        
        if estado not in ['bueno', 'malo']:
            return JsonResponse({
                'success': False,
                'error': 'Estado debe ser "bueno" o "malo"'
            })
        
        # Procesar campos en lote
        resultados = []
        errores = []
        
        with transaction.atomic():
            for campo in campos:
                try:
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
                    
                    resultados.append({
                        'campo': campo,
                        'estado': calificacion.estado,
                        'creado': created
                    })
                    
                except Exception as e:
                    errores.append({
                        'campo': campo,
                        'error': str(e)
                    })
        
        return JsonResponse({
            'success': True,
            'resultados': resultados,
            'errores': errores,
            'total_procesados': len(resultados),
            'total_errores': len(errores)
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
    except OperationalError as e:
        if "database is locked" in str(e).lower():
            return JsonResponse({
                'success': False,
                'error': 'Base de datos ocupada. Intente nuevamente en unos segundos.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })
