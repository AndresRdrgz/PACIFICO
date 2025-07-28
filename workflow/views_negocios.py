from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

from .modelsWorkflow import (
    Solicitud, Pipeline, Etapa, SubEstado, HistorialSolicitud,
    RequisitoSolicitud, CampoPersonalizado, ValorCampoSolicitud,
    PermisoPipeline, PermisoBandeja
)
from pacifico.models import Cliente, Cotizacion


def enrich_solicitud_data(solicitud):
    """
    Enriquece los datos de una solicitud para evitar lógica compleja en el template
    """
    # Calcular clases CSS para prioridad
    priority_classes = {
        'Alta': {'bg': '#fee2e2', 'text': '#dc3545', 'css': 'bg-red-100 text-red-800'},
        'Media': {'bg': '#fef9c3', 'text': '#ffc107', 'css': 'bg-yellow-100 text-yellow-800'},
        'Baja': {'bg': '#dcfce7', 'text': '#198754', 'css': 'bg-green-100 text-green-800'}
    }
    
    # Calcular datos de SLA
    sla_color_map = {
        'text-danger': {'color': '#dc3545', 'css': 'bg-red-500', 'text': 'Vencido', 'data': 'vencido', 'bg': 'bg-danger bg-opacity-10'},
        'text-warning': {'color': '#ffc107', 'css': 'bg-yellow-500', 'text': 'Por vencer', 'data': 'por vencer', 'bg': ''},
        'text-success': {'color': '#198754', 'css': 'bg-green-500', 'text': 'En tiempo', 'data': 'en tiempo', 'bg': ''}
    }
    
    # Función helper para avatar
    def get_user_avatar_data(user):
        if not user:
            return {'type': 'icon', 'content': 'fas fa-user-slash', 'class': 'w-4 h-4 bg-gray-200 rounded-full flex items-center justify-center text-xs font-medium text-gray-500'}
        
        if hasattr(user, 'userprofile') and user.userprofile and hasattr(user.userprofile, 'profile_picture') and user.userprofile.profile_picture:
            return {
                'type': 'image',
                'src': user.userprofile.profile_picture.url,
                'alt': user.get_full_name() or user.username,
                'class': 'w-4 h-4 rounded-full object-cover border'
            }
        
        initial = ''
        if user.first_name:
            initial = user.first_name[0].upper()
        elif user.username:
            initial = user.username[0].upper()
        
        return {
            'type': 'initial',
            'content': initial,
            'class': 'w-4 h-4 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium text-gray-600'
        }
    
    # Enriquecer datos de prioridad
    priority_data = priority_classes.get(solicitud.prioridad, {'bg': 'white', 'text': '#6c757d', 'css': 'bg-gray-100 text-gray-800'})
    
    # Enriquecer datos de SLA
    sla_data = sla_color_map.get(getattr(solicitud, 'sla_color', ''), {'color': '#6c757d', 'css': 'bg-gray-400', 'text': 'N/A', 'data': 'sin sla', 'bg': ''})
    
    # Enriquecer datos de usuarios
    propietario_avatar = get_user_avatar_data(getattr(solicitud, 'propietario_user', None))
    asignado_avatar = get_user_avatar_data(getattr(solicitud, 'asignado_a_user', None))
    
    # Datos enriquecidos
    enriched_data = {
        # Datos de prioridad
        'prioridad_bg_color': priority_data['bg'],
        'prioridad_text_color': priority_data['text'],
        'prioridad_css_class': priority_data['css'],
        
        # Datos de SLA
        'sla_border_color': sla_data['color'],
        'sla_css_class': sla_data['css'],
        'sla_status_text': sla_data['text'],
        'sla_data_attr': sla_data['data'],
        'sla_bg_class': sla_data['bg'],
        
        # Datos de usuarios
        'propietario_avatar': propietario_avatar,
        'asignado_avatar': asignado_avatar,
        'is_unassigned': getattr(solicitud, 'asignado_a', '') == 'Sin asignar' or not getattr(solicitud, 'asignado_a', ''),
        
        # Datos de etiquetas
        'show_digital_badge': getattr(solicitud, 'origen', '') == 'Canal Digital',
        'has_etiquetas': bool(getattr(solicitud, 'etiquetas_oficial', '')),
    }
    
    # Agregar todos los datos enriquecidos al objeto solicitud
    for key, value in enriched_data.items():
        setattr(solicitud, f'enriched_{key}', value)
    
    return solicitud


@login_required
def negocios_view(request):
    """
    Vista principal de negocios con tabla de solicitudes y funcionalidad de drawer
    """
    # Obtener parámetros de filtrado y búsqueda
    search_query = request.GET.get('search', '')
    pipeline_filter = request.GET.get('pipeline', '')
    etapa_filter = request.GET.get('etapa', '')
    estado_filter = request.GET.get('estado', '')
    page = request.GET.get('page', 1)
    
    # Construir queryset base según permisos del usuario
    if request.user.is_superuser:
        # Superuser puede ver todas las solicitudes
        solicitudes = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).prefetch_related(
            'cliente', 'cotizacion'
        ).all()
    else:
        # Usuario regular solo ve sus solicitudes asignadas o creadas
        solicitudes = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).prefetch_related(
            'cliente', 'cotizacion'
        ).filter(
            Q(asignada_a=request.user) | Q(creada_por=request.user)
        )
    
    # Aplicar filtros de búsqueda
    if search_query:
        solicitudes = solicitudes.filter(
            Q(codigo__icontains=search_query) |
            Q(cliente__nombre__icontains=search_query) |
            Q(cliente__cedula__icontains=search_query) |
            Q(cotizacion__producto__icontains=search_query)
        )
    
    if pipeline_filter:
        solicitudes = solicitudes.filter(pipeline_id=pipeline_filter)
    
    if etapa_filter:
        solicitudes = solicitudes.filter(etapa_actual_id=etapa_filter)
    
    if estado_filter:
        solicitudes = solicitudes.filter(subestado_actual_id=estado_filter)
    
    # Ordenar por fecha de última actualización (más recientes primero)
    solicitudes = solicitudes.order_by('-fecha_ultima_actualizacion')
    
    # Paginación
    paginator = Paginator(solicitudes, 25)  # 25 solicitudes por página
    solicitudes_page = paginator.get_page(page)
    
    # Obtener pipelines disponibles para el usuario
    if request.user.is_superuser:
        pipelines_disponibles = Pipeline.objects.all()
    else:
        # Obtener pipelines basado en permisos
        pipelines_disponibles = Pipeline.objects.filter(
            Q(permisopipeline__usuario=request.user) |
            Q(etapas__permisos__grupo__user=request.user)
        ).distinct()
    
    # Obtener etapas para filtros
    etapas_disponibles = Etapa.objects.all()
    
    # Obtener subestados para filtros
    subestados_disponibles = SubEstado.objects.all()
    
    # Calcular estadísticas básicas
    total_solicitudes = solicitudes.count() if hasattr(solicitudes, 'count') else len(solicitudes)
    solicitudes_pendientes = solicitudes.filter(
        etapa_actual__nombre__icontains='pendiente'
    ).count() if hasattr(solicitudes, 'filter') else 0
    
    # Enriquecer datos de solicitudes para el template
    solicitudes_enriched = []
    for solicitud in solicitudes_page:
        enriched = enrich_solicitud_data(solicitud)
        solicitudes_enriched.append(enriched)
    
    context = {
        'solicitudes': solicitudes_enriched,
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'pipelines_disponibles': pipelines_disponibles,
        'etapas_disponibles': etapas_disponibles,
        'subestados_disponibles': subestados_disponibles,
        'search_query': search_query,
        'pipeline_filter': pipeline_filter,
        'etapa_filter': etapa_filter,
        'estado_filter': estado_filter,
        'is_superuser': request.user.is_superuser,
        'user': request.user,
    }
    print(f"Rendering negocios view with {len(solicitudes_enriched)} solicitudes")
    return render(request, 'workflow/negocios.html', context)


@login_required
def api_solicitudes_tabla(request):
    """
    API para obtener datos de solicitudes para la tabla con paginación y filtros
    """
    try:
        # Parámetros de DataTables
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 25))
        search_value = request.GET.get('search[value]', '')
        
        # Obtener solicitudes según permisos
        if request.user.is_superuser:
            solicitudes = Solicitud.objects.select_related(
                'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a', 'cliente', 'cotizacion'
            ).all()
        else:
            solicitudes = Solicitud.objects.select_related(
                'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a', 'cliente', 'cotizacion'
            ).filter(
                Q(asignada_a=request.user) | Q(creada_por=request.user)
            )
        
        # Aplicar búsqueda
        if search_value:
            solicitudes = solicitudes.filter(
                Q(codigo__icontains=search_value) |
                Q(cliente__nombre__icontains=search_value) |
                Q(cliente__cedula__icontains=search_value) |
                Q(cotizacion__producto__icontains=search_value)
            )
        
        # Total de registros
        total_records = solicitudes.count()
        
        # Aplicar paginación
        solicitudes_page = solicitudes[start:start + length]
        
        # Formatear datos para DataTables
        data = []
        for solicitud in solicitudes_page:
            # Calcular SLA
            sla_status = 'verde'
            sla_text = 'En tiempo'
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                tiempo_transcurrido = timezone.now() - solicitud.fecha_ultima_actualizacion
                if tiempo_transcurrido > solicitud.etapa_actual.sla:
                    sla_status = 'rojo'
                    sla_text = 'Vencido'
                elif tiempo_transcurrido > (solicitud.etapa_actual.sla * 0.8):
                    sla_status = 'amarillo'
                    sla_text = 'Por vencer'
            
            # Obtener información del cliente
            cliente_info = {
                'nombre': solicitud.cliente.nombre if solicitud.cliente else 'N/A',
                'cedula': solicitud.cliente.cedula if solicitud.cliente else 'N/A'
            }
            
            # Obtener información de la cotización
            cotizacion_info = {
                'producto': solicitud.cotizacion.producto if solicitud.cotizacion else 'N/A',
                'monto': float(solicitud.cotizacion.monto_financiado) if solicitud.cotizacion and solicitud.cotizacion.monto_financiado else 0
            }
            
            data.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo or f'SOL-{solicitud.id}',
                'cliente_nombre': cliente_info['nombre'],
                'cliente_cedula': cliente_info['cedula'],
                'producto': cotizacion_info['producto'],
                'monto_financiado': cotizacion_info['monto'],
                'propietario': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else 'Sin asignar',
                'etapa': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
                'estado': solicitud.subestado_actual.nombre if solicitud.subestado_actual else 'Sin estado',
                'sla_status': sla_status,
                'sla_text': sla_text,
                'fecha_actualizacion': solicitud.fecha_ultima_actualizacion.strftime('%Y-%m-%d %H:%M'),
                'pipeline': solicitud.pipeline.nombre if solicitud.pipeline else 'N/A'
            })
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener solicitudes: {str(e)}'
        }, status=500)


@login_required
def api_detalle_solicitud_modal(request, solicitud_id):
    """
    API para obtener detalles completos de una solicitud para el modal
    """
    try:
        # Verificar permisos
        if request.user.is_superuser:
            solicitud = get_object_or_404(
                Solicitud.objects.select_related(
                    'pipeline', 'etapa_actual', 'subestado_actual',
                    'creada_por', 'asignada_a', 'cliente', 'cotizacion'
                ),
                id=solicitud_id
            )
        else:
            solicitud = get_object_or_404(
                Solicitud.objects.select_related(
                    'pipeline', 'etapa_actual', 'subestado_actual',
                    'creada_por', 'asignada_a', 'cliente', 'cotizacion'
                ).filter(
                    Q(asignada_a=request.user) | Q(creada_por=request.user)
                ),
                id=solicitud_id
            )
        
        # Obtener historial de la solicitud
        historial = HistorialSolicitud.objects.filter(
            solicitud=solicitud
        ).select_related('usuario').order_by('-fecha_cambio')
        
        # Obtener requisitos de la solicitud
        requisitos = RequisitoSolicitud.objects.filter(
            solicitud=solicitud
        ).select_related('requisito')
        
        # Obtener campos personalizados
        campos_personalizados = ValorCampoSolicitud.objects.filter(
            solicitud=solicitud
        ).select_related('campo')
        
        # Formatear datos
        solicitud_data = {
            'id': solicitud.id,
            'codigo': solicitud.codigo or f'SOL-{solicitud.id}',
            'pipeline': {
                'id': solicitud.pipeline.id,
                'nombre': solicitud.pipeline.nombre
            } if solicitud.pipeline else None,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id,
                'nombre': solicitud.etapa_actual.nombre
            } if solicitud.etapa_actual else None,
            'subestado_actual': {
                'id': solicitud.subestado_actual.id,
                'nombre': solicitud.subestado_actual.nombre
            } if solicitud.subestado_actual else None,
            'cliente': {
                'id': solicitud.cliente.id,
                'nombre': solicitud.cliente.nombre,
                'cedula': solicitud.cliente.cedula,
                'telefono': getattr(solicitud.cliente, 'telefono', ''),
                'email': getattr(solicitud.cliente, 'email', ''),
            } if solicitud.cliente else None,
            'cotizacion': {
                'id': solicitud.cotizacion.id,
                'producto': solicitud.cotizacion.producto,
                'monto_financiado': float(solicitud.cotizacion.monto_financiado) if solicitud.cotizacion.monto_financiado else 0,
                'plazo': getattr(solicitud.cotizacion, 'plazo', 0),
            } if solicitud.cotizacion else None,
            'creada_por': {
                'id': solicitud.creada_por.id,
                'nombre': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
            },
            'asignada_a': {
                'id': solicitud.asignada_a.id,
                'nombre': solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username,
            } if solicitud.asignada_a else None,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
            'prioridad': solicitud.prioridad,
            'etiquetas_oficial': solicitud.etiquetas_oficial,
        }
        
        # Formatear historial
        historial_data = []
        for item in historial:
            historial_data.append({
                'id': item.id,
                'accion': item.accion,
                'descripcion': item.descripcion,
                'usuario': item.usuario.get_full_name() or item.usuario.username if item.usuario else 'Sistema',
                'fecha_cambio': item.fecha_cambio.isoformat(),
                'etapa_anterior': item.etapa_anterior,
                'etapa_nueva': item.etapa_nueva,
            })
        
        # Formatear requisitos
        requisitos_data = []
        for req in requisitos:
            requisitos_data.append({
                'id': req.id,
                'requisito': {
                    'id': req.requisito.id,
                    'nombre': req.requisito.nombre,
                    'descripcion': req.requisito.descripcion,
                    'es_obligatorio': req.requisito.es_obligatorio,
                },
                'estado': req.estado,
                'observaciones': req.observaciones,
                'archivo_url': req.archivo.url if req.archivo else None,
                'fecha_subida': req.fecha_subida.isoformat() if req.fecha_subida else None,
            })
        
        # Formatear campos personalizados
        campos_data = []
        for campo in campos_personalizados:
            campos_data.append({
                'id': campo.id,
                'campo': {
                    'id': campo.campo.id,
                    'nombre': campo.campo.nombre,
                    'tipo': campo.campo.tipo,
                },
                'valor': campo.valor,
            })
        
        return JsonResponse({
            'success': True,
            'solicitud': solicitud_data,
            'historial': historial_data,
            'requisitos': requisitos_data,
            'campos_personalizados': campos_data,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener detalles de la solicitud: {str(e)}'
        }, status=500)


@login_required
def api_estadisticas_negocios(request):
    """
    API para obtener estadísticas para el dashboard de negocios
    """
    try:
        # Obtener solicitudes según permisos
        if request.user.is_superuser:
            solicitudes = Solicitud.objects.all()
        else:
            solicitudes = Solicitud.objects.filter(
                Q(asignada_a=request.user) | Q(creada_por=request.user)
            )
        
        # Calcular estadísticas
        total_solicitudes = solicitudes.count()
        solicitudes_pendientes = solicitudes.filter(
            etapa_actual__nombre__icontains='pendiente'
        ).count()
        solicitudes_aprobadas = solicitudes.filter(
            etapa_actual__nombre__icontains='aprobad'
        ).count()
        solicitudes_rechazadas = solicitudes.filter(
            etapa_actual__nombre__icontains='rechazad'
        ).count()
        
        # Solicitudes por pipeline
        pipelines_stats = {}
        if request.user.is_superuser:
            pipelines = Pipeline.objects.all()
        else:
            pipelines = Pipeline.objects.filter(
                Q(permisopipeline__usuario=request.user) |
                Q(etapas__permisos__grupo__user=request.user)
            ).distinct()
        
        for pipeline in pipelines:
            count = solicitudes.filter(pipeline=pipeline).count()
            pipelines_stats[pipeline.nombre] = count
        
        return JsonResponse({
            'success': True,
            'estadisticas': {
                'total_solicitudes': total_solicitudes,
                'solicitudes_pendientes': solicitudes_pendientes,
                'solicitudes_aprobadas': solicitudes_aprobadas,
                'solicitudes_rechazadas': solicitudes_rechazadas,
                'pipelines_stats': pipelines_stats,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener estadísticas: {str(e)}'
        }, status=500)


@login_required
def api_solicitudes(request):
    """API para obtener solicitudes según permisos del usuario"""
    
    # Obtener solicitudes según permisos del usuario
    if request.user.is_superuser:
        solicitudes = Solicitud.objects.all().select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a'
        )
    else:
        solicitudes = Solicitud.objects.filter(
            Q(asignada_a=request.user) | Q(creada_por=request.user)
        ).select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a'
        )
    
    # Filtros
    pipeline_id = request.GET.get('pipeline')
    if pipeline_id:
        solicitudes = solicitudes.filter(pipeline_id=pipeline_id)
    
    estado = request.GET.get('estado')
    if estado == 'activas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=False)
    elif estado == 'completadas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=True)
    
    # Serializar datos
    datos = []
    for solicitud in solicitudes:
        datos.append({
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'pipeline': solicitud.pipeline.nombre,
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
            'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
            'creada_por': solicitud.creada_por.username,
            'asignada_a': solicitud.asignada_a.username if solicitud.asignada_a else None,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
        })
    
    return JsonResponse({'solicitudes': datos})


@login_required  
def api_estadisticas(request):
    """API para obtener estadísticas globales"""
    
    # Obtener solicitudes según permisos del usuario
    if request.user.is_superuser:
        solicitudes_base = Solicitud.objects.all()
    else:
        solicitudes_base = Solicitud.objects.filter(
            Q(asignada_a=request.user) | Q(creada_por=request.user)
        )
    
    # Estadísticas básicas
    total_solicitudes = solicitudes_base.count()
    solicitudes_activas = solicitudes_base.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = solicitudes_base.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    if request.user.is_superuser:
        pipelines = Pipeline.objects.all()
    else:
        pipelines = Pipeline.objects.filter(
            Q(permisopipeline__usuario=request.user) |
            Q(etapas__permisos__grupo__user=request.user)
        ).distinct()
    
    solicitudes_por_pipeline = []
    for pipeline in pipelines:
        total = solicitudes_base.filter(pipeline=pipeline).count()
        solicitudes_por_pipeline.append({
            'nombre': pipeline.nombre,
            'total': total
        })
    
    # Solicitudes vencidas - Calculamos usando Python para compatibilidad con SQLite
    solicitudes_vencidas = 0
    for solicitud in solicitudes_base.filter(etapa_actual__isnull=False).select_related('etapa_actual'):
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_limite = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            if timezone.now() > fecha_limite:
                solicitudes_vencidas += 1
    
    return JsonResponse({
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': solicitudes_por_pipeline,
    })
