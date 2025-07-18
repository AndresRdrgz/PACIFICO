from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .modelsWorkflow import Solicitud, Etapa, ParticipacionComite, NivelComite, UsuarioNivelComite
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models

@login_required
def bandeja_comite_view(request):
    """
    Renderiza la bandeja de trabajo del Comité de Crédito.
    """
    
    # Por ahora, solo superuser puede ver todo.
    # La lógica de permisos por nivel se implementará en la API.
    if not request.user.is_superuser:
        # Aquí iría la lógica para usuarios que no son superusuarios
        # Por ejemplo, verificar si pertenecen a algún nivel del comité.
        pass

    # Obtener la etapa "Comité de Crédito" (usar filter().first() para evitar MultipleObjectsReturned)
    try:
        etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
        if etapa_comite:
            # Calcular la cantidad de solicitudes en la etapa del comité
            total_solicitudes = Solicitud.objects.filter(etapa_actual=etapa_comite).count()
        else:
            total_solicitudes = 0
    except Exception as e:
        # Si hay algún error, mostrar mensaje y establecer valores por defecto
        messages.error(request, f'Error al obtener las solicitudes del comité: {str(e)}')
        etapa_comite = None
        total_solicitudes = 0

    context = {
        'etapa_comite': etapa_comite,
        'total_solicitudes': total_solicitudes,
        'page_title': 'Bandeja del Comité de Crédito',
        'page_description': 'Solicitudes pendientes de revisión y aprobación por el comité.'
    }
    
    return render(request, 'workflow/bandeja_comite.html', context)


@login_required
def detalle_solicitud_comite(request, solicitud_id):
    """
    Vista especializada para el detalle de solicitudes en el comité de crédito
    """
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud esté en etapa de comité
    if solicitud.etapa_actual.nombre != "Comité de Crédito":
        messages.error(request, 'Esta solicitud no está en la etapa del comité.')
        return redirect('workflow:bandeja_comite')
    
    # Verificar que el usuario pertenece a algún nivel del comité
    nivel_usuario = UsuarioNivelComite.objects.filter(
        usuario=request.user, 
        activo=True
    ).first()
    
    if not nivel_usuario and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para ver solicitudes del comité.')
        return redirect('workflow:bandeja_comite')
    
    # Obtener información básica de la solicitud
    cliente = solicitud.cliente if hasattr(solicitud, 'cliente') else None
    cotizacion = solicitud.cotizacion if hasattr(solicitud, 'cotizacion') else None
    historial = solicitud.historial.all().order_by('-fecha_inicio')
    requisitos = solicitud.requisitos.all().select_related('requisito')
    
    # Obtener participaciones del comité para esta solicitud
    participaciones = ParticipacionComite.objects.filter(
        solicitud=solicitud
    ).select_related('usuario', 'nivel', 'usuario__userprofile').order_by('nivel__orden', '-fecha_modificacion')
    
    # Obtener todos los niveles del comité ordenados por jerarquía
    niveles_comite = NivelComite.objects.all().order_by('orden')
    
    # Verificar si el usuario ya participó
    participacion_usuario = None
    if nivel_usuario:
        participacion_usuario = ParticipacionComite.objects.filter(
            solicitud=solicitud,
            usuario=request.user,
            nivel=nivel_usuario.nivel
        ).first()
    
    # Obtener solicitudes relacionadas (por cédula del cliente, excluyendo la actual)
    solicitudes_relacionadas = []
    mostrar_mensaje_sin_cliente = False
    cedula_cliente = None
    
    # Obtener cédula desde cliente o cotización
    if solicitud.cliente and solicitud.cliente.cedulaCliente:
        cedula_cliente = solicitud.cliente.cedulaCliente
    elif solicitud.cotizacion and solicitud.cotizacion.cedulaCliente:
        cedula_cliente = solicitud.cotizacion.cedulaCliente
    
    if cedula_cliente:
        # Buscar todas las solicitudes con la misma cédula (en cliente o cotización)
        solicitudes_relacionadas = Solicitud.objects.filter(
            (models.Q(cliente__cedulaCliente=cedula_cliente) | 
             models.Q(cotizacion__cedulaCliente=cedula_cliente))
        ).exclude(id=solicitud.id).select_related('cotizacion', 'cliente').order_by('-fecha_creacion')
    else:
        mostrar_mensaje_sin_cliente = True
    
    # Calcular información de progreso
    etapas_pipeline = solicitud.pipeline.etapas.all().order_by('orden')
    total_etapas = etapas_pipeline.count()
    if total_etapas > 0:
        etapa_actual_orden = solicitud.etapa_actual.orden if solicitud.etapa_actual else 0
        progreso_porcentaje = (etapa_actual_orden / total_etapas) * 100
    else:
        progreso_porcentaje = 0
    
    context = {
        'solicitud': solicitud,
        'cliente': cliente,
        'cotizacion': cotizacion,
        'historial': historial,
        'requisitos': requisitos,
        'participaciones': participaciones,
        'niveles_comite': niveles_comite,
        'nivel_usuario': nivel_usuario,
        'participacion_usuario': participacion_usuario,
        'etapas_pipeline': etapas_pipeline,
        'progreso_porcentaje': progreso_porcentaje,
        'solicitudes_relacionadas': solicitudes_relacionadas,
        'mostrar_mensaje_sin_cliente': mostrar_mensaje_sin_cliente,
        'timestamp': timezone.now().timestamp(),
    }
    
    return render(request, 'workflow/detalle_solicitud_comite.html', context) 