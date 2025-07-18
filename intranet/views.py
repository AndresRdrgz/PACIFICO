from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Sala, Reserva, Participante
from .api import (
    obtener_salas_disponibles, crear_reserva, obtener_reservas,
    cancelar_reserva, confirmar_asistencia, obtener_usuarios, validar_conflicto
)


@login_required
def dashboard_intranet(request):
    """
    Vista principal del dashboard de intranet.
    
    Muestra un resumen de las reservas del usuario y acceso
    a las diferentes funcionalidades del sistema.
    """
    # Obtener reservas del usuario (como organizador y participante)
    mis_reservas = Reserva.objects.filter(
        usuario_creador=request.user,
        estado='activa',
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:5]
    
    # Reservas donde soy participante
    reservas_participante = Reserva.objects.filter(
        participante__usuario=request.user,
        estado='activa',
        fecha_inicio__gte=timezone.now()
    ).exclude(usuario_creador=request.user).order_by('fecha_inicio')[:5]
    
    # Próximas reservas de hoy
    hoy = timezone.now().date()
    reservas_hoy = Reserva.objects.filter(
        fecha_inicio__date=hoy,
        estado='activa'
    ).order_by('fecha_inicio')
    
    # Estadísticas
    total_reservas_creadas = Reserva.objects.filter(
        usuario_creador=request.user
    ).count()
    
    total_participaciones = Participante.objects.filter(
        usuario=request.user
    ).count()
    
    salas_disponibles = Sala.objects.filter(estado='activa').count()
    
    context = {
        'mis_reservas': mis_reservas,
        'reservas_participante': reservas_participante,
        'reservas_hoy': reservas_hoy,
        'total_reservas_creadas': total_reservas_creadas,
        'total_participaciones': total_participaciones,
        'salas_disponibles': salas_disponibles,
        'hoy': hoy,
    }
    
    return render(request, 'intranet/dashboard.html', context)


@login_required
def calendario_reservas(request):
    """
    Vista del calendario de reservas.
    
    Muestra un calendario interactivo donde los usuarios pueden
    ver todas las reservas y crear nuevas.
    """
    # Obtener parámetros de filtro
    sala_id = request.GET.get('sala_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Obtener salas disponibles para el filtro
    salas = Sala.objects.filter(estado='activa').order_by('nombre')
    
    # Si se especifica una sala, obtener solo las reservas de esa sala
    if sala_id:
        sala_seleccionada = get_object_or_404(Sala, id=sala_id)
        reservas = Reserva.objects.filter(
            sala=sala_seleccionada,
            estado='activa'
        ).select_related('sala', 'usuario_creador').prefetch_related(
            'participante_set__usuario'
        )
    else:
        sala_seleccionada = None
        reservas = Reserva.objects.filter(
            estado='activa'
        ).select_related('sala', 'usuario_creador').prefetch_related(
            'participante_set__usuario'
        )
    
    # Aplicar filtros de fecha si se especifican
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            reservas = reservas.filter(fecha_inicio__date__gte=fecha_inicio.date())
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            reservas = reservas.filter(fecha_inicio__date__lte=fecha_fin.date())
        except ValueError:
            pass
    
    # Ordenar por fecha de inicio
    reservas = reservas.order_by('fecha_inicio')
    
    context = {
        'salas': salas,
        'sala_seleccionada': sala_seleccionada,
        'reservas': reservas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'intranet/calendario.html', context)


@login_required
def nueva_reserva(request):
    """
    Vista para crear una nueva reserva.
    
    Formulario para seleccionar sala, fecha, hora y participantes.
    """
    if request.method == 'POST':
        # Procesar el formulario
        try:
            # Los datos se procesan via AJAX en el frontend
            # Esta vista solo maneja la renderización del formulario
            pass
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {str(e)}')
    
    # Obtener salas disponibles
    salas = Sala.objects.filter(estado='activa').order_by('nombre')
    
    # Obtener usuarios disponibles para invitaciones
    from django.contrib.auth.models import User
    usuarios = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'salas': salas,
        'usuarios': usuarios,
    }
    
    return render(request, 'intranet/nueva_reserva.html', context)


@login_required
def mis_reservas(request):
    """
    Vista para mostrar las reservas del usuario.
    
    Incluye reservas creadas por el usuario y donde es participante.
    """
    # Reservas creadas por el usuario
    reservas_creadas = Reserva.objects.filter(
        usuario_creador=request.user
    ).select_related('sala').prefetch_related(
        'participante_set__usuario'
    ).order_by('-fecha_inicio')
    
    # Reservas donde el usuario es participante
    reservas_participante = Reserva.objects.filter(
        participante__usuario=request.user
    ).exclude(usuario_creador=request.user).select_related(
        'sala', 'usuario_creador'
    ).prefetch_related(
        'participante_set__usuario'
    ).order_by('-fecha_inicio')
    
    # Filtrar por estado si se especifica
    estado = request.GET.get('estado')
    if estado:
        reservas_creadas = reservas_creadas.filter(estado=estado)
        reservas_participante = reservas_participante.filter(estado=estado)
    
    # Filtrar por sala si se especifica
    sala_id = request.GET.get('sala_id')
    if sala_id:
        reservas_creadas = reservas_creadas.filter(sala_id=sala_id)
        reservas_participante = reservas_participante.filter(sala_id=sala_id)
    
    context = {
        'reservas_creadas': reservas_creadas,
        'reservas_participante': reservas_participante,
        'estado_filtro': estado,
        'sala_filtro': sala_id,
    }
    
    return render(request, 'intranet/mis_reservas.html', context)


@login_required
def detalle_reserva(request, reserva_id):
    """
    Vista para mostrar los detalles de una reserva específica.
    
    Args:
        reserva_id (str): ID de la reserva a mostrar
    """
    reserva = get_object_or_404(
        Reserva.objects.select_related('sala', 'usuario_creador').prefetch_related(
            'participante_set__usuario'
        ),
        id=reserva_id
    )
    
    # Verificar si el usuario tiene acceso a esta reserva
    es_organizador = reserva.usuario_creador == request.user
    es_participante = reserva.participante_set.filter(usuario=request.user).exists()
    
    if not (es_organizador or es_participante):
        messages.error(request, 'No tienes permisos para ver esta reserva.')
        return redirect('intranet:mis_reservas')
    
    # Obtener el estado de participación del usuario actual
    estado_participacion = None
    if es_participante:
        participante = reserva.participante_set.get(usuario=request.user)
        estado_participacion = participante.estado_asistencia
    
    context = {
        'reserva': reserva,
        'es_organizador': es_organizador,
        'es_participante': es_participante,
        'estado_participacion': estado_participacion,
        'participantes': reserva.get_participantes(),
    }
    
    return render(request, 'intranet/detalle_reserva.html', context)


@login_required
def gestion_salas(request):
    """
    Vista para la gestión de salas (solo administradores).
    
    Permite crear, editar y gestionar las salas de trabajo.
    """
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('intranet:dashboard')
    
    salas = Sala.objects.all().order_by('nombre')
    
    # Calcular estadísticas
    salas_activas = salas.filter(estado='activa').count()
    salas_inactivas = salas.filter(estado='inactiva').count()
    salas_mantenimiento = salas.filter(estado='mantenimiento').count()
    
    context = {
        'salas': salas,
        'salas_activas': salas_activas,
        'salas_inactivas': salas_inactivas,
        'salas_mantenimiento': salas_mantenimiento,
    }
    
    return render(request, 'intranet/gestion_salas.html', context)


@login_required
def api_salas_disponibles(request):
    """
    Endpoint API para obtener salas disponibles.
    Redirige a la función del archivo api.py
    """
    return obtener_salas_disponibles(request)


@login_required
def api_crear_reserva(request):
    """
    Endpoint API para crear una nueva reserva.
    Redirige a la función del archivo api.py
    """
    return crear_reserva(request)


@login_required
def api_obtener_reservas(request):
    """
    Endpoint API para obtener reservas.
    Redirige a la función del archivo api.py
    """
    return obtener_reservas(request)


@login_required
def api_cancelar_reserva(request):
    """
    Endpoint API para cancelar una reserva.
    Redirige a la función del archivo api.py
    """
    return cancelar_reserva(request)


@login_required
def api_confirmar_asistencia(request):
    """
    Endpoint API para confirmar asistencia.
    Redirige a la función del archivo api.py
    """
    return confirmar_asistencia(request)


@login_required
def api_obtener_usuarios(request):
    """
    Endpoint API para obtener usuarios disponibles.
    Redirige a la función del archivo api.py
    """
    return obtener_usuarios(request)


@login_required
def api_validar_conflicto(request):
    """
    Endpoint API para validar conflictos de horario.
    Redirige a la función del archivo api.py
    """
    return validar_conflicto(request) 