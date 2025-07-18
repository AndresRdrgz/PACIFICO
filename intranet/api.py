import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import Sala, Reserva, Participante, Notificacion


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def obtener_salas_disponibles(request):
    """
    Obtiene todas las salas disponibles para reservas.
    
    Returns:
        JsonResponse: Lista de salas con su información básica
    """
    try:
        salas = Sala.objects.filter(estado='activa').values(
            'id', 'nombre', 'ubicacion', 'capacidad', 'descripcion', 'equipamiento'
        )
        
        # Agregar URL de la foto si existe
        for sala in salas:
            sala_obj = Sala.objects.get(id=sala['id'])
            if sala_obj.foto:
                sala['foto_url'] = sala_obj.foto.url
            else:
                sala['foto_url'] = None
        
        return JsonResponse({
            'success': True,
            'salas': list(salas)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def crear_reserva(request):
    """
    Crea una nueva reserva de sala.
    
    Expected JSON data:
    {
        "sala_id": "uuid",
        "titulo": "string",
        "descripcion": "string",
        "fecha_inicio": "YYYY-MM-DD HH:MM",
        "fecha_fin": "YYYY-MM-DD HH:MM",
        "participantes": ["user_id1", "user_id2", ...]
    }
    
    Returns:
        JsonResponse: Resultado de la operación
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['sala_id', 'titulo', 'fecha_inicio', 'fecha_fin']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }, status=400)
        
        # Obtener la sala
        try:
            sala = Sala.objects.get(id=data['sala_id'])
        except Sala.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Sala no encontrada'
            }, status=404)
        
        # Verificar que la sala esté disponible
        if not sala.esta_disponible:
            return JsonResponse({
                'success': False,
                'error': 'La sala no está disponible para reservas'
            }, status=400)
        
        # Parsear fechas
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d %H:%M')
            fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d %H:%M')
            
            # Convertir a timezone aware
            fecha_inicio = timezone.make_aware(fecha_inicio)
            fecha_fin = timezone.make_aware(fecha_fin)
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido. Use: YYYY-MM-DD HH:MM'
            }, status=400)
        
        # Verificar que la fecha de fin sea posterior a la de inicio
        if fecha_fin <= fecha_inicio:
            return JsonResponse({
                'success': False,
                'error': 'La fecha de fin debe ser posterior a la fecha de inicio'
            }, status=400)
        
        # Verificar conflictos de horario
        conflictos = sala.get_reservas_activas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        if conflictos.exists():
            conflicto = conflictos.first()
            return JsonResponse({
                'success': False,
                'error': 'La sala ya está reservada en este horario',
                'conflicto': {
                    'titulo': conflicto.titulo,
                    'organizador': f"{conflicto.usuario_creador.first_name} {conflicto.usuario_creador.last_name}",
                    'fecha_inicio': conflicto.fecha_inicio.strftime('%Y-%m-%d %H:%M'),
                    'fecha_fin': conflicto.fecha_fin.strftime('%Y-%m-%d %H:%M'),
                    'participantes': [
                        {
                            'nombre': p.usuario.get_full_name(),
                            'email': p.usuario.email
                        } for p in conflicto.get_participantes()
                    ]
                }
            }, status=409)
        
        # Crear la reserva
        reserva = Reserva.objects.create(
            sala=sala,
            usuario_creador=request.user,
            titulo=data['titulo'],
            descripcion=data.get('descripcion', ''),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        # Agregar participantes
        participantes_ids = data.get('participantes', [])
        participantes_ids.append(request.user.id)  # El creador siempre es participante
        
        for user_id in set(participantes_ids):  # Usar set para evitar duplicados
            try:
                usuario = User.objects.get(id=user_id)
                participante = Participante.objects.create(
                    reserva=reserva,
                    usuario=usuario
                )
                
                # Enviar notificación por email
                enviar_notificacion_invitacion(reserva, usuario)
                
            except User.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'reserva_id': str(reserva.id),
            'message': 'Reserva creada exitosamente'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def obtener_reservas(request):
    """
    Obtiene las reservas según los filtros especificados.
    
    Query parameters:
    - sala_id: Filtrar por sala específica
    - fecha_inicio: Fecha de inicio (YYYY-MM-DD)
    - fecha_fin: Fecha de fin (YYYY-MM-DD)
    - usuario_id: Filtrar por usuario específico
    - estado: Filtrar por estado de la reserva
    
    Returns:
        JsonResponse: Lista de reservas con información detallada
    """
    try:
        reservas = Reserva.objects.select_related('sala', 'usuario_creador').prefetch_related(
            'participante_set__usuario'
        )
        
        # Aplicar filtros
        sala_id = request.GET.get('sala_id')
        if sala_id:
            reservas = reservas.filter(sala_id=sala_id)
        
        fecha_inicio = request.GET.get('fecha_inicio')
        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_inicio = timezone.make_aware(fecha_inicio)
                reservas = reservas.filter(fecha_inicio__date__gte=fecha_inicio.date())
            except ValueError:
                pass
        
        fecha_fin = request.GET.get('fecha_fin')
        if fecha_fin:
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
                fecha_fin = timezone.make_aware(fecha_fin)
                reservas = reservas.filter(fecha_inicio__date__lte=fecha_fin.date())
            except ValueError:
                pass
        
        usuario_id = request.GET.get('usuario_id')
        if usuario_id:
            reservas = reservas.filter(usuario_creador_id=usuario_id)
        
        estado = request.GET.get('estado')
        if estado:
            reservas = reservas.filter(estado=estado)
        
        # Ordenar por fecha de inicio
        reservas = reservas.order_by('fecha_inicio')
        
        # Serializar las reservas
        reservas_data = []
        for reserva in reservas:
            reserva_data = {
                'id': str(reserva.id),
                'titulo': reserva.titulo,
                'descripcion': reserva.descripcion,
                'fecha_inicio': reserva.fecha_inicio.strftime('%Y-%m-%d %H:%M'),
                'fecha_fin': reserva.fecha_fin.strftime('%Y-%m-%d %H:%M'),
                'estado': reserva.estado,
                'duracion_minutos': reserva.duracion_minutos,
                'sala': {
                    'id': str(reserva.sala.id),
                    'nombre': reserva.sala.nombre,
                    'ubicacion': reserva.sala.ubicacion,
                    'capacidad': reserva.sala.capacidad
                },
                'organizador': {
                    'id': reserva.usuario_creador.id,
                    'nombre': reserva.usuario_creador.get_full_name(),
                    'email': reserva.usuario_creador.email
                },
                'participantes': [
                    {
                        'id': p.usuario.id,
                        'nombre': p.usuario.get_full_name(),
                        'email': p.usuario.email,
                        'estado_asistencia': p.estado_asistencia
                    } for p in reserva.get_participantes()
                ]
            }
            reservas_data.append(reserva_data)
        
        return JsonResponse({
            'success': True,
            'reservas': reservas_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cancelar_reserva(request):
    """
    Cancela una reserva existente.
    
    Expected JSON data:
    {
        "reserva_id": "uuid"
    }
    
    Returns:
        JsonResponse: Resultado de la operación
    """
    try:
        data = json.loads(request.body)
        reserva_id = data.get('reserva_id')
        
        if not reserva_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de reserva requerido'
            }, status=400)
        
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Reserva no encontrada'
            }, status=404)
        
        # Verificar permisos (solo el creador puede cancelar)
        if reserva.usuario_creador != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para cancelar esta reserva'
            }, status=403)
        
        # Cancelar la reserva
        reserva.cancelar()
        
        # Notificar a los participantes
        for participante in reserva.get_participantes():
            enviar_notificacion_cancelacion(reserva, participante.usuario)
        
        return JsonResponse({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def confirmar_asistencia(request):
    """
    Confirma o declina la asistencia a una reserva.
    
    Expected JSON data:
    {
        "reserva_id": "uuid",
        "confirmar": true/false
    }
    
    Returns:
        JsonResponse: Resultado de la operación
    """
    try:
        data = json.loads(request.body)
        reserva_id = data.get('reserva_id')
        confirmar = data.get('confirmar', True)
        
        if not reserva_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de reserva requerido'
            }, status=400)
        
        try:
            participante = Participante.objects.get(
                reserva_id=reserva_id,
                usuario=request.user
            )
        except Participante.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No eres participante de esta reserva'
            }, status=404)
        
        if confirmar:
            participante.confirmar_asistencia()
            mensaje = 'Asistencia confirmada'
        else:
            participante.declinar_asistencia()
            mensaje = 'Asistencia declinada'
        
        return JsonResponse({
            'success': True,
            'message': mensaje
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def enviar_notificacion_invitacion(reserva, usuario):
    """
    Envía una notificación de invitación por email.
    
    Args:
        reserva (Reserva): La reserva para la cual se envía la invitación
        usuario (User): El usuario destinatario
    """
    try:
        subject = f'Invitación a reunión: {reserva.titulo}'
        
        context = {
            'usuario': usuario,
            'reserva': reserva,
            'organizador': reserva.usuario_creador,
            'sala': reserva.sala,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }
        
        html_message = render_to_string('intranet/emails/invitacion.html', context)
        plain_message = render_to_string('intranet/emails/invitacion.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Registrar la notificación
        Notificacion.objects.create(
            reserva=reserva,
            tipo='invitacion',
            destinatario=usuario,
            email_enviado=usuario.email,
            estado='enviado'
        )
        
    except Exception as e:
        # Registrar el error
        Notificacion.objects.create(
            reserva=reserva,
            tipo='invitacion',
            destinatario=usuario,
            email_enviado=usuario.email,
            estado='error',
            error_mensaje=str(e)
        )


def enviar_notificacion_cancelacion(reserva, usuario):
    """
    Envía una notificación de cancelación por email.
    
    Args:
        reserva (Reserva): La reserva cancelada
        usuario (User): El usuario destinatario
    """
    try:
        subject = f'Cancelación de reunión: {reserva.titulo}'
        
        context = {
            'usuario': usuario,
            'reserva': reserva,
            'organizador': reserva.usuario_creador,
            'sala': reserva.sala,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
        }
        
        html_message = render_to_string('intranet/emails/cancelacion.html', context)
        plain_message = render_to_string('intranet/emails/cancelacion.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Registrar la notificación
        Notificacion.objects.create(
            reserva=reserva,
            tipo='cancelacion',
            destinatario=usuario,
            email_enviado=usuario.email,
            estado='enviado'
        )
        
    except Exception as e:
        # Registrar el error
        Notificacion.objects.create(
            reserva=reserva,
            tipo='cancelacion',
            destinatario=usuario,
            email_enviado=usuario.email,
            estado='error',
            error_mensaje=str(e)
        )


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def obtener_usuarios(request):
    """
    Obtiene la lista de usuarios disponibles para invitaciones.
    
    Returns:
        JsonResponse: Lista de usuarios con información básica
    """
    try:
        usuarios = User.objects.filter(is_active=True).values(
            'id', 'username', 'first_name', 'last_name', 'email'
        )
        
        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario['id'],
                'nombre': f"{usuario['first_name']} {usuario['last_name']}".strip(),
                'username': usuario['username'],
                'email': usuario['email']
            })
        
        return JsonResponse({
            'success': True,
            'usuarios': usuarios_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def validar_conflicto(request):
    """
    Valida si existe un conflicto de horario para una sala en un período específico.
    
    Expected JSON data:
    {
        "sala_id": "uuid",
        "fecha_inicio": "YYYY-MM-DDTHH:MM",
        "fecha_fin": "YYYY-MM-DDTHH:MM"
    }
    
    Returns:
        JsonResponse: Resultado de la validación
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['sala_id', 'fecha_inicio', 'fecha_fin']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }, status=400)
        
        # Obtener la sala
        try:
            sala = Sala.objects.get(id=data['sala_id'])
        except Sala.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Sala no encontrada'
            }, status=404)
        
        # Parsear fechas
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%dT%H:%M')
            fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%dT%H:%M')
            
            # Convertir a timezone aware
            fecha_inicio = timezone.make_aware(fecha_inicio)
            fecha_fin = timezone.make_aware(fecha_fin)
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido. Use: YYYY-MM-DDTHH:MM'
            }, status=400)
        
        # Verificar que la fecha de fin sea posterior a la de inicio
        if fecha_fin <= fecha_inicio:
            return JsonResponse({
                'success': False,
                'error': 'La fecha de fin debe ser posterior a la fecha de inicio'
            }, status=400)
        
        # Verificar conflictos de horario
        conflictos = sala.get_reservas_activas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        if conflictos.exists():
            conflicto = conflictos.first()
            return JsonResponse({
                'success': True,
                'conflicto': True,
                'mensaje': 'La sala ya está reservada en este horario',
                'detalles': f"""
                    <div class="mt-2 p-3 bg-red-100 rounded">
                        <p><strong>Reserva existente:</strong> {conflicto.titulo}</p>
                        <p><strong>Organizador:</strong> {conflicto.usuario_creador.get_full_name()}</p>
                        <p><strong>Horario:</strong> {conflicto.fecha_inicio.strftime('%d/%m/%Y %H:%M')} - {conflicto.fecha_fin.strftime('%H:%M')}</p>
                        <p><strong>Participantes:</strong></p>
                        <ul class="ml-4">
                            {''.join([f'<li>• {p.usuario.get_full_name()} ({p.usuario.email})</li>' for p in conflicto.get_participantes()])}
                        </ul>
                    </div>
                """
            })
        
        return JsonResponse({
            'success': True,
            'conflicto': False,
            'mensaje': 'No hay conflictos de horario'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 