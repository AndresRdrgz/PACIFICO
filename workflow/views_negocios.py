from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from .modelsWorkflow import (
    Pipeline, Etapa, SubEstado, Solicitud, HistorialSolicitud,
    PermisoPipeline, PermisoEtapa, NotaRecordatorio
)
from pacifico.models import Cliente, Cotizacion
from django.contrib.auth.models import User, Group

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
    
    # Obtener información de recordatorios
    recordatorios = solicitud.notas_recordatorios.filter(
        tipo='recordatorio',
        es_activo=True
    )
    
    # Calcular estadísticas de recordatorios
    total_recordatorios = recordatorios.count()
    recordatorios_pendientes = recordatorios.filter(estado='pendiente').count()
    recordatorios_vencidos = 0
    recordatorios_proximos_vencer = 0
    
    # Verificar recordatorios vencidos y próximos a vencer usando las propiedades del modelo
    for recordatorio in recordatorios.filter(estado='pendiente'):
        if recordatorio.esta_vencido:
            recordatorios_vencidos += 1
        elif recordatorio.proximo_a_vencer:
            recordatorios_proximos_vencer += 1
    
    # También contar los que ya tienen estado 'vencido'
    recordatorios_vencidos += recordatorios.filter(estado='vencido').count()
    
    # Agregar datos de recordatorios
    solicitud.recordatorios_info = {
        'total': total_recordatorios,
        'pendientes': recordatorios_pendientes,
        'vencidos': recordatorios_vencidos,
        'proximos_vencer': recordatorios_proximos_vencer,
        'tiene_recordatorios': total_recordatorios > 0,
        'tiene_pendientes': recordatorios_pendientes > 0,
        'tiene_vencidos': recordatorios_vencidos > 0,
        'tiene_proximos_vencer': recordatorios_proximos_vencer > 0
    }
    
    # Determinar el estado visual del indicador de recordatorios
    if recordatorios_vencidos > 0:
        solicitud.recordatorios_status = 'danger'  # Rojo para vencidos
        solicitud.recordatorios_icon = 'fas fa-exclamation-triangle'
        solicitud.recordatorios_title = f"{recordatorios_vencidos} recordatorio(s) vencido(s)"
    elif recordatorios_proximos_vencer > 0:
        solicitud.recordatorios_status = 'warning'  # Amarillo para próximos a vencer
        solicitud.recordatorios_icon = 'fas fa-clock'
        solicitud.recordatorios_title = f"{recordatorios_proximos_vencer} recordatorio(s) próximo(s) a vencer"
    elif recordatorios_pendientes > 0:
        solicitud.recordatorios_status = 'info'  # Azul para pendientes
        solicitud.recordatorios_icon = 'fas fa-bell'
        solicitud.recordatorios_title = f"{recordatorios_pendientes} recordatorio(s) pendiente(s)"
    else:
        solicitud.recordatorios_status = None
        solicitud.recordatorios_icon = None
        solicitud.recordatorios_title = None
    
    # Agregar propiedades adicionales para el template
    # Cliente information
    solicitud.cliente_nombre = solicitud.cliente_nombre_completo
    solicitud.cliente_cedula = solicitud.cliente_cedula_completa
    
    # Estado information
    if solicitud.subestado_actual:
        solicitud.estado_actual = solicitud.subestado_actual.nombre
        solicitud.estado_color = 'primary'  # Default color
    else:
        solicitud.estado_actual = 'Sin estado'
        solicitud.estado_color = 'secondary'
    
    # SLA information
    if solicitud.etapa_actual and solicitud.etapa_actual.sla:
        # Get the historial entry for the current etapa to calculate SLA from the correct start date
        historial_actual = solicitud.historial.filter(etapa=solicitud.etapa_actual).order_by('-fecha_inicio').first()
        if historial_actual:
            tiempo_transcurrido = timezone.now() - historial_actual.fecha_inicio
            tiempo_restante = solicitud.etapa_actual.sla - tiempo_transcurrido
            
            if tiempo_transcurrido > solicitud.etapa_actual.sla:
                solicitud.sla_color = 'text-danger'
                solicitud.sla_restante = 'Vencido'
                # Calculate overdue time
                tiempo_vencido = tiempo_transcurrido - solicitud.etapa_actual.sla
                horas_vencidas = int(tiempo_vencido.total_seconds() // 3600)
                minutos_vencidos = int((tiempo_vencido.total_seconds() % 3600) // 60)
                solicitud.sla_tiempo_restante = f"+{horas_vencidas}h {minutos_vencidos}m"
            elif tiempo_transcurrido > (solicitud.etapa_actual.sla * 0.8):
                solicitud.sla_color = 'text-warning'
                solicitud.sla_restante = 'Por vencer'
                # Calculate remaining time
                horas_restantes = int(tiempo_restante.total_seconds() // 3600)
                minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
                solicitud.sla_tiempo_restante = f"{horas_restantes}h {minutos_restantes}m"
            else:
                solicitud.sla_color = 'text-success'
                solicitud.sla_restante = 'En tiempo'
                # Calculate remaining time
                horas_restantes = int(tiempo_restante.total_seconds() // 3600)
                minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
                solicitud.sla_tiempo_restante = f"{horas_restantes}h {minutos_restantes}m"
        else:
            solicitud.sla_color = 'text-muted'
            solicitud.sla_restante = 'N/A'
            solicitud.sla_tiempo_restante = 'N/A'
    else:
        solicitud.sla_color = 'text-muted'
        solicitud.sla_restante = 'N/A'
        solicitud.sla_tiempo_restante = 'N/A'
    
    # Propietario is already available as solicitud.propietario
    
    # Ensure basic fields are accessible
    if not hasattr(solicitud, 'id') or solicitud.id is None:
        if hasattr(solicitud, 'pk') and solicitud.pk is not None:
            solicitud.id = solicitud.pk
        else:
            print(f"⚠️  WARNING: Solicitud has no valid ID or PK: {solicitud}")
            return None  # Return None for invalid solicitudes
    
    return solicitud


@login_required
def negocios_view(request):
    """
    Vista principal de negocios con tabla de solicitudes y funcionalidad de drawer
    Con redirección automática al último pipeline seleccionado
    """
    # Obtener parámetros de filtrado y búsqueda
    search_query = request.GET.get('search', '')
    pipeline_filter = request.GET.get('pipeline', '')
    etapa_filter = request.GET.get('etapa', '')
    estado_filter = request.GET.get('estado', '')
    page = request.GET.get('page', '1')  # Keep as string for consistency
    
    # NUEVA FUNCIONALIDAD: Redirección automática al último pipeline seleccionado
    session_key = f'negocios_last_pipeline_{request.user.id}'
    
    # Debug logging
    print(f"🔍 DEBUG: search_query='{search_query}', etapa_filter='{etapa_filter}', estado_filter='{estado_filter}', page='{page}'")
    print(f"🔍 DEBUG: pipeline_filter='{pipeline_filter}', session_key in session: {session_key in request.session}")
    if session_key in request.session:
        print(f"🔍 DEBUG: saved pipeline: {request.session[session_key]}")
    
    # Si hay un pipeline_filter, guardarlo en la sesión
    if pipeline_filter:
        request.session[session_key] = pipeline_filter
        print(f"🔄 Guardando pipeline {pipeline_filter} en sesión para usuario {request.user.username}")
    
    # Si NO hay filtros y existe un pipeline guardado en sesión, redirigir
    elif not any([search_query, etapa_filter, estado_filter, page != '1']) and session_key in request.session:
        last_pipeline = request.session[session_key]
        print(f"🚀 Redirigiendo usuario {request.user.username} al último pipeline: {last_pipeline}")
        
        # Verificar que el pipeline aún existe y el usuario tiene acceso
        try:
            if request.user.is_superuser:
                pipeline_exists = Pipeline.objects.filter(id=last_pipeline).exists()
            else:
                pipeline_exists = Pipeline.objects.filter(
                    Q(id=last_pipeline) &
                    (Q(permisos_pipeline__usuario=request.user) |
                     Q(etapas__permisos__grupo__user=request.user))
                ).exists()
            
            if pipeline_exists:
                # Construir URL con el pipeline filter
                redirect_url = f"{reverse('workflow:negocios')}?pipeline={last_pipeline}"
                return redirect(redirect_url)
            else:
                # Si el pipeline ya no existe o no tiene acceso, limpiar la sesión
                del request.session[session_key]
                print(f"⚠️  Pipeline {last_pipeline} ya no existe o sin acceso - limpiando sesión")
        except (ValueError, TypeError):
            # Si el pipeline_id no es válido, limpiar la sesión
            del request.session[session_key]
            print(f"⚠️  Pipeline ID inválido en sesión - limpiando")
    
    # Construir queryset base según permisos del usuario
    if request.user.is_superuser:
        # Superuser puede ver todas las solicitudes
        solicitudes = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).prefetch_related(
            'cliente', 'cotizacion', 'notas_recordatorios'
        ).all()
    else:
        # Usuario regular solo ve sus solicitudes asignadas o creadas
        solicitudes = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).prefetch_related(
            'cliente', 'cotizacion', 'notas_recordatorios'
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
    solicitudes_page = paginator.get_page(int(page))
    
    # Obtener pipelines disponibles para el usuario
    if request.user.is_superuser:
        pipelines_disponibles = Pipeline.objects.all()
        print(f"🔍 DEBUG: Superuser {request.user} accessing pipelines")
        print(f"🔍 DEBUG: Found {pipelines_disponibles.count()} pipelines total")
        for p in pipelines_disponibles:
            print(f"    - {p.nombre} (ID: {p.pk})")
    else:
        # Obtener pipelines basado en permisos
        pipelines_disponibles = Pipeline.objects.filter(
            Q(permisos_pipeline__usuario=request.user) |
            Q(etapas__permisos__grupo__user=request.user)
        ).distinct()
        print(f"🔍 DEBUG: Regular user {request.user} accessing pipelines")
        print(f"🔍 DEBUG: Found {pipelines_disponibles.count()} pipelines with permissions")
    
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
        # Debug: Check for missing IDs
        if not hasattr(solicitud, 'id') or solicitud.id is None:
            print(f"⚠️  WARNING: Found solicitud without valid ID: {solicitud}")
            print(f"    - PK: {getattr(solicitud, 'pk', 'None')}")
            print(f"    - Cliente: {getattr(solicitud, 'cliente_nombre', 'Unknown')}")
            continue  # Skip solicitudes without valid IDs
           
        enriched = enrich_solicitud_data(solicitud)
        if enriched is not None:  # Only add valid enriched solicitudes
            solicitudes_enriched.append(enriched)
    
    # Get current pipeline if filter is applied
    current_pipeline = None
    if pipeline_filter:
        try:
            current_pipeline = Pipeline.objects.get(id=pipeline_filter)
        except Pipeline.DoesNotExist:
            pass
    
    # Prepare Kanban-specific data structure
    solicitudes_por_etapa = {}
    view_type = request.GET.get('view', 'table')
    
    if view_type == 'kanban' and current_pipeline:
        print(f"🎯 DEBUG: Preparing Kanban data for pipeline {current_pipeline.nombre}")
        print(f"🎯 DEBUG: Pipeline has {current_pipeline.etapas.count()} stages")
        
        # Initialize dictionary with all pipeline stages
        for etapa in current_pipeline.etapas.all():
            solicitudes_por_etapa[etapa.id] = []
            print(f"    - Stage: {etapa.nombre} (ID: {etapa.id})")
        
        # Group solicitudes by their current stage
        for solicitud in solicitudes_enriched:
            if solicitud.etapa_actual and solicitud.etapa_actual.id in solicitudes_por_etapa:
                solicitudes_por_etapa[solicitud.etapa_actual.id].append(solicitud)
                print(f"    - Added solicitud {solicitud.codigo} to stage {solicitud.etapa_actual.nombre}")
            else:
                # Handle solicitudes without a current stage
                if 'sin_etapa' not in solicitudes_por_etapa:
                    solicitudes_por_etapa['sin_etapa'] = []
                solicitudes_por_etapa['sin_etapa'].append(solicitud)
                print(f"    - Added solicitud {solicitud.codigo} to 'sin_etapa'")
        
        print(f"🎯 DEBUG: Final solicitudes_por_etapa structure:")
        for etapa_id, solicitudes_list in solicitudes_por_etapa.items():
            print(f"    - Etapa {etapa_id}: {len(solicitudes_list)} solicitudes")
    
    context = {
        'solicitudes': solicitudes_enriched,
        'solicitudes_tabla': solicitudes_enriched,  # Template expects this variable name
        'solicitudes_por_etapa': solicitudes_por_etapa,  # For Kanban view
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'pipelines_disponibles': pipelines_disponibles,
        'pipelines': pipelines_disponibles,  # Template compatibility
        'pipeline': current_pipeline,  # Current selected pipeline
        'etapas_disponibles': etapas_disponibles,
        'subestados_disponibles': subestados_disponibles,
        'search_query': search_query,
        'pipeline_filter': pipeline_filter,
        'etapa_filter': etapa_filter,
        'estado_filter': estado_filter,
        'is_superuser': request.user.is_superuser,
        'user': request.user,
        'no_access': False,  # Explicitly set to False for access
        'view_type': view_type,  # Pass view type to template
        'last_pipeline_saved': session_key in request.session,  # Info for frontend
        'last_pipeline_id': request.session.get(session_key, None),  # ID del último pipeline
    }
    print(f"🔍 DEBUG: Context being passed to template:")
    print(f"    - pipelines_disponibles: {len(context['pipelines_disponibles'])} items")
    print(f"    - pipelines: {len(context['pipelines'])} items")
    print(f"    - current pipeline: {context['pipeline']}")
    print(f"    - solicitudes: {len(context['solicitudes'])} items")
    print(f"    - solicitudes_tabla: {len(context['solicitudes_tabla'])} items")
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
                # Client data from cotization for SURA prefilling
                'nombreCliente': getattr(solicitud.cotizacion, 'nombreCliente', ''),
                'cedulaCliente': getattr(solicitud.cotizacion, 'cedulaCliente', ''),
                'tipoDocumento': getattr(solicitud.cotizacion, 'tipoDocumento', 'CEDULA'),
                # Car data from cotization for SURA prefilling  
                'marca': getattr(solicitud.cotizacion, 'marca', ''),
                'modelo': getattr(solicitud.cotizacion, 'modelo', ''),
                'yearCarro': getattr(solicitud.cotizacion, 'yearCarro', ''),
                'valorAuto': float(getattr(solicitud.cotizacion, 'valorAuto', 0)) if getattr(solicitud.cotizacion, 'valorAuto', None) else 0,
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
                Q(permisos_pipeline__usuario=request.user) |
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
    
    try:
        # Obtener solicitudes según permisos del usuario
        if request.user.is_superuser:
            solicitudes = Solicitud.objects.all().select_related(
                'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a', 
                'cliente', 'cotizacion'
            )
        else:
            solicitudes = Solicitud.objects.filter(
                Q(asignada_a=request.user) | Q(creada_por=request.user)
            ).select_related(
                'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a',
                'cliente', 'cotizacion'
            )
        
        # Filtro por ID específico (para obtener una solicitud)
        solicitud_id = request.GET.get('id')
        if solicitud_id:
            solicitudes = solicitudes.filter(id=solicitud_id)
        
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
            # Obtener nombre del cliente de diferentes fuentes
            cliente_nombre = 'N/A'
            cedula_cliente = ''
            
            if solicitud.cliente:
                cliente_nombre = solicitud.cliente.nombreCliente or 'Sin nombre'
                cedula_cliente = solicitud.cliente.cedulaCliente or ''
            elif solicitud.cotizacion and hasattr(solicitud.cotizacion, 'cliente') and solicitud.cotizacion.cliente:
                cliente_nombre = solicitud.cotizacion.cliente.nombreCliente or 'Sin nombre'
                cedula_cliente = solicitud.cotizacion.cliente.cedulaCliente or ''
            elif solicitud.cotizacion:
                # Fallback to cotization client fields
                cliente_nombre = solicitud.cotizacion.nombreCliente or 'Sin cliente'
                cedula_cliente = solicitud.cotizacion.cedulaCliente or ''
            elif solicitud.apc_no_cedula:
                # Fallback para solicitudes APC sin cliente asociado
                cliente_nombre = 'Cliente APC'
                cedula_cliente = solicitud.apc_no_cedula
            elif hasattr(solicitud, 'sura_no_documento') and solicitud.sura_no_documento:
                # Fallback para solicitudes SURA sin cliente asociado  
                cliente_nombre = 'Cliente SURA'
                cedula_cliente = solicitud.sura_no_documento
            
            # Datos de cotización si existe
            cotizacion_data = {}
            if solicitud.cotizacion:
                cotizacion_data = {
                    'marca': getattr(solicitud.cotizacion, 'marca', ''),
                    'modelo': getattr(solicitud.cotizacion, 'modelo', ''),
                    'yearCarro': getattr(solicitud.cotizacion, 'yearCarro', ''),
                    'valorAuto': getattr(solicitud.cotizacion, 'valorAuto', ''),
                    'placa': getattr(solicitud.cotizacion, 'placa', ''),
                }
            
            datos.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'pipeline': solicitud.pipeline.nombre,
                'pipeline_id': solicitud.pipeline.id,
                'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Completada',
                'etapa_actual_id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
                'creada_por': solicitud.creada_por.username,
                'asignada_a': solicitud.asignada_a.username if solicitud.asignada_a else None,
                'fecha_creacion': solicitud.fecha_creacion.isoformat(),
                'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
                
                # Información del cliente (campos nuevos)
                'cliente_nombre': cliente_nombre,
                'nombreCliente': cliente_nombre,  # Alias para compatibilidad
                'cedulaCliente': cedula_cliente,
                'apc_no_cedula': solicitud.apc_no_cedula or '',
                'apc_tipo_documento': solicitud.apc_tipo_documento or '',
                'apc_status': solicitud.apc_status or '',
                
                # Información de cotización
                **cotizacion_data,
                
                # Campos antiguos para compatibilidad
                'cliente': cliente_nombre,
                'documento': cedula_cliente,
            })
        
        return JsonResponse({'solicitudes': datos})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


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
            Q(permisos_pipeline__usuario=request.user) |
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


@login_required
def api_clear_saved_pipeline(request):
    """
    API para limpiar el pipeline guardado en la sesión del usuario
    """
    if request.method == 'POST':
        session_key = f'negocios_last_pipeline_{request.user.id}'
        
        if session_key in request.session:
            pipeline_id = request.session[session_key]
            del request.session[session_key]
            print(f"🗑️  Pipeline {pipeline_id} eliminado de la sesión para usuario {request.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Pipeline guardado eliminado exitosamente',
                'cleared_pipeline_id': pipeline_id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No hay pipeline guardado en la sesión'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


@login_required
def api_get_saved_pipeline(request):
    """
    API para obtener información del pipeline guardado en la sesión
    """
    session_key = f'negocios_last_pipeline_{request.user.id}'
    
    if session_key in request.session:
        pipeline_id = request.session[session_key]
        
        try:
            # Verificar que el pipeline existe y el usuario tiene acceso
            if request.user.is_superuser:
                pipeline = Pipeline.objects.get(id=pipeline_id)
            else:
                pipeline = Pipeline.objects.filter(
                    Q(id=pipeline_id) &
                    (Q(permisos_pipeline__usuario=request.user) |
                     Q(etapas__permisos__grupo__user=request.user))
                ).first()
            
            if pipeline:
                return JsonResponse({
                    'has_saved_pipeline': True,
                    'pipeline_id': pipeline_id,
                    'pipeline_name': pipeline.nombre,
                    'redirect_url': f"{reverse('workflow:negocios')}?pipeline={pipeline_id}"
                })
            else:
                # Pipeline no existe o sin acceso, limpiar sesión
                del request.session[session_key]
                return JsonResponse({
                    'has_saved_pipeline': False,
                    'message': 'Pipeline guardado ya no disponible'
                })
                
        except (Pipeline.DoesNotExist, ValueError, TypeError):
            # Pipeline inválido, limpiar sesión
            del request.session[session_key]
            return JsonResponse({
                'has_saved_pipeline': False,
                'message': 'Pipeline guardado inválido'
            })
    
    return JsonResponse({
        'has_saved_pipeline': False,
        'message': 'No hay pipeline guardado'
    })
