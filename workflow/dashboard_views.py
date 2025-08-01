from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Count, Avg, ExpressionWrapper, fields
from django.db.models.functions import Now, Extract
from django.utils import timezone
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta
from .modelsWorkflow import (
    Solicitud, HistorialSolicitud, Pipeline, Etapa, RequisitoSolicitud,
    ParticipacionComite, SolicitudEscalamientoComite, NivelComite,
    PermisoEtapa, PermisoBandeja, NotaRecordatorio
)
from .models import CalificacionCampo
from pacifico.models import Cotizacion


@login_required
def dashboard_operativo(request):
    """
    Dashboard operativo optimizado con filtros avanzados y métricas detalladas
    Compatible con SQLite y PostgreSQL
    """
    print("DEBUG: Dashboard operativo llamado")
    
    # ==========================================
    # FILTROS DE LA REQUEST
    # ==========================================
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Filtros de pipeline y etapa
    pipeline_id = request.GET.get('pipeline')
    etapa_id = request.GET.get('etapa')
    usuario_id = request.GET.get('usuario')
    prioridad = request.GET.get('prioridad')
    estado_sla = request.GET.get('estado_sla')  # 'vencido', 'vigente', 'todos'
    
    # ==========================================
    # QUERYSET BASE OPTIMIZADO
    # ==========================================
    
    # Base queryset con select_related para evitar N+1 queries
    queryset = Solicitud.objects.select_related(
        'pipeline', 
        'etapa_actual', 
        'subestado_actual', 
        'creada_por', 
        'asignada_a'
    ).prefetch_related('historial')
    
    # Aplicar filtros de fecha
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
        except ValueError:
            pass
    
    # Filtros adicionales
    if pipeline_id:
        queryset = queryset.filter(pipeline_id=pipeline_id)
    
    if etapa_id:
        queryset = queryset.filter(etapa_actual_id=etapa_id)
    
    if usuario_id:
        queryset = queryset.filter(asignada_a_id=usuario_id)
    
    if prioridad:
        queryset = queryset.filter(prioridad=prioridad)
    
    # ==========================================
    # CÁLCULO DE SLA VENCIDO (COMPATIBLE CON SQLITE)
    # ==========================================
    
    # Anotar tiempo en etapa actual
    queryset = queryset.annotate(
        tiempo_en_etapa=ExpressionWrapper(
            Now() - F('fecha_ultima_actualizacion'),
            output_field=fields.DurationField()
        )
    )
    
    # Calcular SLA vencido usando Python en lugar de DB
    solicitudes_con_sla = []
    solicitudes_vencidas = 0
    solicitudes_vigentes = 0
    total_solicitudes = 0
    
    for solicitud in queryset:
        total_solicitudes += 1
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            tiempo_actual = timezone.now() - solicitud.fecha_ultima_actualizacion
            sla_vencido = tiempo_actual > solicitud.etapa_actual.sla
            solicitud.sla_vencido = sla_vencido
            if sla_vencido:
                solicitudes_vencidas += 1
            else:
                solicitudes_vigentes += 1
        else:
            solicitud.sla_vencido = False
            solicitudes_vigentes += 1
        
        solicitudes_con_sla.append(solicitud)
    
    # Calcular porcentaje de vencidas
    porcentaje_vencidas = (solicitudes_vencidas / total_solicitudes * 100) if total_solicitudes > 0 else 0
    
    # Filtrar por estado de SLA
    if estado_sla == 'vencido':
        solicitudes_con_sla = [s for s in solicitudes_con_sla if s.sla_vencido]
    elif estado_sla == 'vigente':
        solicitudes_con_sla = [s for s in solicitudes_con_sla if not s.sla_vencido]
    
    # ==========================================
    # MÉTRICAS PRINCIPALES
    # ==========================================
    
    # Total de solicitudes encontradas
    total_solicitudes = len(solicitudes_con_sla)
    
    # Solicitudes vigentes
    solicitudes_vigentes = total_solicitudes - solicitudes_vencidas
    
    # Porcentaje de vencidas
    porcentaje_vencidas = (solicitudes_vencidas / total_solicitudes * 100) if total_solicitudes > 0 else 0
    
    # ==========================================
    # SOLICITUDES POR ETAPA (AGRUPADO)
    # ==========================================
    
    solicitudes_por_etapa = {}
    for solicitud in solicitudes_con_sla:
        etapa_nombre = solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin Etapa'
        
        if etapa_nombre not in solicitudes_por_etapa:
            solicitudes_por_etapa[etapa_nombre] = {
                'total': 0,
                'vencidas': 0
            }
        
        solicitudes_por_etapa[etapa_nombre]['total'] += 1
        if solicitud.sla_vencido:
            solicitudes_por_etapa[etapa_nombre]['vencidas'] += 1
    
    # Convertir a lista para el template
    solicitudes_por_etapa_list = [
        {
            'etapa_actual__nombre': etapa,
            'total': data['total'],
            'vencidas': data['vencidas']
        }
        for etapa, data in solicitudes_por_etapa.items()
    ]
    
    # Ordenar por total descendente
    solicitudes_por_etapa_list.sort(key=lambda x: x['total'], reverse=True)
    
    # ==========================================
    # TIEMPO POR ETAPA - ANÁLISIS DETALLADO
    # ==========================================
    
    # 1. HISTORIAL POR SOLICITUD INDIVIDUAL
    historiales_individuales = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).select_related('etapa', 'solicitud').order_by('-fecha_inicio')[:100]  # Limitado para rendimiento
    
    # Calcular duración y SLA para cada historial
    historiales_con_duracion = []
    for historial in historiales_individuales:
        duracion = historial.fecha_fin - historial.fecha_inicio
        duracion_horas = duracion.total_seconds() / 3600  # Convertir a horas
        
        # Evaluar si cumplió SLA
        sla_cumplido = False
        if historial.etapa and historial.etapa.sla:
            sla_horas = historial.etapa.sla.total_seconds() / 3600
            sla_cumplido = duracion_horas <= sla_horas
        
        historiales_con_duracion.append({
            'solicitud_codigo': historial.solicitud.codigo if historial.solicitud else 'N/A',
            'etapa_nombre': historial.etapa.nombre if historial.etapa else 'Sin Etapa',
            'fecha_inicio': historial.fecha_inicio,
            'fecha_fin': historial.fecha_fin,
            'duracion_horas': duracion_horas,
            'duracion_formateada': f"{int(duracion_horas)}h {int((duracion_horas % 1) * 60)}m",
            'sla_cumplido': sla_cumplido,
            'sla_etapa_horas': historial.etapa.sla.total_seconds() / 3600 if historial.etapa and historial.etapa.sla else 0,
            'sla_etapa_formateado': f"{int(historial.etapa.sla.total_seconds() / 3600)}h {int((historial.etapa.sla.total_seconds() / 3600 % 1) * 60)}m" if historial.etapa and historial.etapa.sla else 'N/A'
        })
    
    # 2. PROMEDIO GLOBAL POR ETAPA
    historiales_completados = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).select_related('etapa')
    
    # Agrupar por etapa
    estadisticas_por_etapa = {}
    for historial in historiales_completados:
        etapa_nombre = historial.etapa.nombre if historial.etapa else 'Sin Etapa'
        duracion = historial.fecha_fin - historial.fecha_inicio
        duracion_horas = duracion.total_seconds() / 3600
        
        # Evaluar SLA
        sla_cumplido = False
        sla_etapa_horas = 0
        if historial.etapa and historial.etapa.sla:
            sla_etapa_horas = historial.etapa.sla.total_seconds() / 3600
            sla_cumplido = duracion_horas <= sla_etapa_horas
        
        if etapa_nombre not in estadisticas_por_etapa:
            estadisticas_por_etapa[etapa_nombre] = {
                'total_duraciones': 0,
                'count': 0,
                'sla_cumplidas': 0,
                'sla_etapa_horas': sla_etapa_horas
            }
        
        estadisticas_por_etapa[etapa_nombre]['total_duraciones'] += duracion_horas
        estadisticas_por_etapa[etapa_nombre]['count'] += 1
        if sla_cumplido:
            estadisticas_por_etapa[etapa_nombre]['sla_cumplidas'] += 1
    
    # Calcular promedios y porcentajes
    promedios_etapa = []
    for etapa_nombre, data in estadisticas_por_etapa.items():
        if data['count'] > 0:
            promedio_horas = data['total_duraciones'] / data['count']
            porcentaje_sla = (data['sla_cumplidas'] / data['count']) * 100
            
            promedios_etapa.append({
                'etapa__nombre': etapa_nombre,
                'dias_promedio': promedio_horas / 24,  # Mantener compatibilidad
                'promedio_horas': promedio_horas,
                'promedio_formateado': f"{int(promedio_horas)}h {int((promedio_horas % 1) * 60)}m",
                'sla_etapa_horas': data['sla_etapa_horas'],
                'sla_etapa_formateado': f"{int(data['sla_etapa_horas'])}h {int((data['sla_etapa_horas'] % 1) * 60)}m" if data['sla_etapa_horas'] > 0 else 'N/A',
                'porcentaje_sla_cumplido': porcentaje_sla,
                'total_casos': data['count'],
                'sla_cumplidas': data['sla_cumplidas']
            })
    
    # Ordenar por nombre de etapa
    promedios_etapa.sort(key=lambda x: x['etapa__nombre'])
    
    # ==========================================
    # TOP 5 USUARIOS CON MÁS SOLICITUDES
    # ==========================================
    
    # Agrupar por usuario
    usuarios_stats = {}
    for solicitud in solicitudes_con_sla:
        if solicitud.asignada_a:
            username = solicitud.asignada_a.username
            full_name = solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username
            
            if username not in usuarios_stats:
                usuarios_stats[username] = {
                    'username': username,
                    'full_name': full_name,
                    'total_solicitudes': 0,
                    'solicitudes_vencidas': 0
                }
            
            usuarios_stats[username]['total_solicitudes'] += 1
            if solicitud.sla_vencido:
                usuarios_stats[username]['solicitudes_vencidas'] += 1
    
    # Convertir a lista y ordenar
    top_usuarios = list(usuarios_stats.values())
    top_usuarios.sort(key=lambda x: x['total_solicitudes'], reverse=True)
    top_usuarios = top_usuarios[:5]  # Top 5
    
    # ==========================================
    # CALIFICACIONES DE COMPLIANCE
    # ==========================================
    
    # Resumen de calificaciones de campos de compliance
    calificaciones_compliance = CalificacionCampo.objects.values(
        'estado'
    ).annotate(
        total=Count('id')
    ).order_by('estado')
    
    # ==========================================
    # MÉTRICAS POR USUARIO - NUEVA SECCIÓN
    # ==========================================
    
    # 1. TOTAL DE SOLICITUDES ASIGNADAS POR USUARIO
    solicitudes_por_usuario = Solicitud.objects.filter(
        asignada_a__isnull=False
    ).values(
        'asignada_a__username',
        'asignada_a__first_name',
        'asignada_a__last_name'
    ).annotate(
        total_asignadas=Count('id'),
        solicitudes_activas=Count('id', filter=Q(etapa_actual__isnull=False)),
        solicitudes_vencidas=Count('id', filter=Q(
            etapa_actual__isnull=False
        ))
    ).order_by('-total_asignadas')[:10]  # Top 10 usuarios
    
    # Convertir QuerySet a lista
    solicitudes_por_usuario = list(solicitudes_por_usuario)
    
    # Calcular SLA vencido por usuario (usando Python para compatibilidad)
    for usuario_data in solicitudes_por_usuario:
        usuario_id = User.objects.get(username=usuario_data['asignada_a__username']).id
        solicitudes_usuario = Solicitud.objects.filter(
            asignada_a_id=usuario_id,
            etapa_actual__isnull=False
        ).select_related('etapa_actual')
        
        vencidas = 0
        for solicitud in solicitudes_usuario:
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                tiempo_actual = timezone.now() - solicitud.fecha_ultima_actualizacion
                if tiempo_actual > solicitud.etapa_actual.sla:
                    vencidas += 1
        
        usuario_data['solicitudes_vencidas'] = vencidas
        usuario_data['porcentaje_vencidas'] = (vencidas / usuario_data['solicitudes_activas'] * 100) if usuario_data['solicitudes_activas'] > 0 else 0
        usuario_data['full_name'] = f"{usuario_data['asignada_a__first_name'] or ''} {usuario_data['asignada_a__last_name'] or ''}".strip() or usuario_data['asignada_a__username']
    
    # 2. PROMEDIO DE TIEMPO POR USUARIO
    tiempo_por_usuario = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False,
        usuario_responsable__isnull=False
    ).values(
        'usuario_responsable__username',
        'usuario_responsable__first_name',
        'usuario_responsable__last_name'
    ).annotate(
        total_historiales=Count('id'),
        duracion_promedio=Avg(
            ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        )
    ).order_by('duracion_promedio')[:10]  # Top 10 más rápidos
    
    # Convertir QuerySet a lista para serialización JSON
    tiempo_por_usuario = list(tiempo_por_usuario)
    
    # Convertir duración a horas para mejor visualización
    for tiempo_data in tiempo_por_usuario:
        if tiempo_data['duracion_promedio']:
            duracion_horas = tiempo_data['duracion_promedio'].total_seconds() / 3600
            tiempo_data['duracion_horas'] = round(duracion_horas, 2)
            tiempo_data['duracion_formateada'] = f"{int(duracion_horas)}h {int((duracion_horas % 1) * 60)}m"
        else:
            tiempo_data['duracion_horas'] = 0
            tiempo_data['duracion_formateada'] = '0h 0m'
        
        tiempo_data['full_name'] = f"{tiempo_data['usuario_responsable__first_name'] or ''} {tiempo_data['usuario_responsable__last_name'] or ''}".strip() or tiempo_data['usuario_responsable__username']
    
    # 3. RANKING DE USUARIOS CON MÁS SOLICITUDES ACTIVAS
    ranking_usuarios_activos = Solicitud.objects.filter(
        asignada_a__isnull=False,
        etapa_actual__isnull=False
    ).values(
        'asignada_a__username',
        'asignada_a__first_name',
        'asignada_a__last_name'
    ).annotate(
        solicitudes_activas=Count('id')
    ).order_by('-solicitudes_activas')[:10]
    
    # Convertir QuerySet a lista
    ranking_usuarios_activos = list(ranking_usuarios_activos)
    
    for ranking_data in ranking_usuarios_activos:
        ranking_data['full_name'] = f"{ranking_data['asignada_a__first_name'] or ''} {ranking_data['asignada_a__last_name'] or ''}".strip() or ranking_data['asignada_a__username']
    
    # 4. TRANSICIONES REALIZADAS POR USUARIO
    transiciones_por_usuario = HistorialSolicitud.objects.filter(
        usuario_responsable__isnull=False
    ).values(
        'usuario_responsable__username',
        'usuario_responsable__first_name',
        'usuario_responsable__last_name'
    ).annotate(
        total_transiciones=Count('id'),
        transiciones_completadas=Count('id', filter=Q(fecha_fin__isnull=False))
    ).order_by('-total_transiciones')[:10]
    
    # Convertir QuerySet a lista
    transiciones_por_usuario = list(transiciones_por_usuario)
    
    for transicion_data in transiciones_por_usuario:
        transicion_data['full_name'] = f"{transicion_data['usuario_responsable__first_name'] or ''} {transicion_data['usuario_responsable__last_name'] or ''}".strip() or transicion_data['usuario_responsable__username']
        transicion_data['porcentaje_completadas'] = (transicion_data['transiciones_completadas'] / transicion_data['total_transiciones'] * 100) if transicion_data['total_transiciones'] > 0 else 0
    
    # ==========================================
    # DATOS PARA FILTROS
    # ==========================================
    
    # Pipelines disponibles
    pipelines = list(Pipeline.objects.all())
    
    # Etapas disponibles
    etapas = list(Etapa.objects.all())
    
    # Usuarios disponibles
    usuarios = list(User.objects.filter(is_active=True).order_by('username'))

    # ==========================================
    # DATOS PARA GRÁFICAS
    # ==========================================
    
    # Datos para Chart.js - Distribución por etapa
    chart_data = {
        'labels': [item['etapa_actual__nombre'] for item in solicitudes_por_etapa_list] if solicitudes_por_etapa_list else [],
        'datasets': [{
            'label': 'Total Solicitudes',
            'data': [item['total'] for item in solicitudes_por_etapa_list] if solicitudes_por_etapa_list else [],
            'backgroundColor': [
                '#28a745', '#ffc107', '#dc3545', '#17a2b8', 
                '#6f42c1', '#fd7e14', '#20c997', '#e83e8c'
            ]
        }]
    }
    
    # Datos para gráfica de SLA vencido
    sla_chart_data = {
        'labels': ['SLA Vigente', 'SLA Vencido'],
        'datasets': [{
            'label': 'Estado SLA',
            'data': [solicitudes_vigentes, solicitudes_vencidas],
            'backgroundColor': ['#28a745', '#dc3545']
        }]
    }
    
    # Datos para gráfica de duración vs SLA
    duracion_chart_data = {
        'labels': [etapa['etapa__nombre'] for etapa in promedios_etapa] if promedios_etapa else [],
        'datasets': [
            {
                'label': 'Duración Promedio (horas)',
                'data': [etapa['promedio_horas'] for etapa in promedios_etapa] if promedios_etapa else [],
                'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2
            },
            {
                'label': 'SLA Etapa (horas)',
                'data': [etapa['sla_etapa_horas'] for etapa in promedios_etapa] if promedios_etapa else [],
                'backgroundColor': 'rgba(255, 99, 132, 0.8)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 2
            }
        ]
    }
    
    # 5. DATOS PARA GRÁFICAS DE USUARIO
    usuarios_chart_data = {
        'labels': [usuario['full_name'] for usuario in solicitudes_por_usuario] if solicitudes_por_usuario else [],
        'datasets': [{
            'label': 'Solicitudes Asignadas',
            'data': [usuario['total_asignadas'] for usuario in solicitudes_por_usuario] if solicitudes_por_usuario else [],
            'backgroundColor': [
                '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1',
                '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#28a745'
            ]
        }]
    }
    
    tiempo_chart_data = {
        'labels': [tiempo['full_name'] for tiempo in tiempo_por_usuario] if tiempo_por_usuario else [],
        'datasets': [{
            'label': 'Duración Promedio (horas)',
            'data': [tiempo['duracion_horas'] for tiempo in tiempo_por_usuario] if tiempo_por_usuario else [],
            'backgroundColor': 'rgba(54, 162, 235, 0.8)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 2
        }]
    }

    # ==========================================
    # CONTEXT OPTIMIZADO
    # ==========================================
    
    context = {
        # Filtros aplicados
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'pipeline_id': pipeline_id,
            'etapa_id': etapa_id,
            'usuario_id': usuario_id,
            'prioridad': prioridad,
            'estado_sla': estado_sla,
        },
        
        # Métricas principales
        'total_solicitudes': total_solicitudes,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_vigentes': solicitudes_vigentes,
        'porcentaje_vencidas': porcentaje_vencidas,
        
        # Datos agrupados
        'solicitudes_por_etapa': solicitudes_por_etapa_list,
        'promedios_etapa': promedios_etapa,
        'top_usuarios': top_usuarios,
        'calificaciones_compliance': calificaciones_compliance,
        
        # Datos de tiempo por etapa
        'historiales_con_duracion': historiales_con_duracion,
        
        # Datos por usuario
        'solicitudes_por_usuario': solicitudes_por_usuario,
        'tiempo_por_usuario': tiempo_por_usuario,
        'ranking_usuarios_activos': ranking_usuarios_activos,
        'transiciones_por_usuario': transiciones_por_usuario,
        
        # Datos para filtros
        'pipelines': pipelines,
        'etapas': etapas,
        'usuarios': usuarios,
        'prioridades': Solicitud.PRIORIDAD_CHOICES,
        
        # Datos para gráficas
        'chart_data': chart_data,
        'sla_chart_data': sla_chart_data,
        'duracion_chart_data': duracion_chart_data,
        'usuarios_chart_data': usuarios_chart_data,
        'tiempo_chart_data': tiempo_chart_data,
        
        # Solicitudes para tabla (limitado a 50 para rendimiento)
        'solicitudes': solicitudes_con_sla[:50],
        
        # ==========================================
        # DATOS DE CUMPLIMIENTO PARA EL BLOQUE
        # ==========================================
        
        # Calificaciones de campos
        'datos_cumplimiento': {
            'buenos': 0,
            'malos': 0,
            'sin_calificar': 0,
            'porcentaje_cumplimiento': 0,
            'requisitos_cumplidos': 0,
            'requisitos_pendientes': 0,
            'top_solicitudes_observadas': [],
            'total_campos': 0,
        },
    }
    
    print("DEBUG: Context creado con éxito")
    print("DEBUG: Total solicitudes:", total_solicitudes)
    print("DEBUG: Solicitudes por usuario:", len(solicitudes_por_usuario))
    
    return render(request, 'workflow/dashboard.html', context) 


@login_required
def dashboard_usuario(request):
    """
    Dashboard específico para análisis por usuario
    """
    print("DEBUG: Dashboard por usuario llamado")
    
    # Filtros básicos
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    pipeline_id = request.GET.get('pipeline_id', '')
    usuario_id = request.GET.get('usuario_id', '')
    
    # Base queryset
    queryset = Solicitud.objects.select_related(
        'pipeline', 'etapa_actual', 'subestado_actual', 'asignada_a'
    )
    
    # Aplicar filtros
    if fecha_inicio:
        queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
    if pipeline_id:
        queryset = queryset.filter(pipeline_id=pipeline_id)
    if usuario_id:
        queryset = queryset.filter(asignada_a_id=usuario_id)
    
    # ==========================================
    # ESTADÍSTICAS ESPECÍFICAS POR USUARIO
    # ==========================================
    
    # 1. RENDIMIENTO POR USUARIO
    rendimiento_usuarios = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False,
        usuario_responsable__isnull=False
    ).values(
        'usuario_responsable__username',
        'usuario_responsable__first_name',
        'usuario_responsable__last_name'
    ).annotate(
        total_solicitudes=Count('id'),
        tiempo_promedio=Avg(
            ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        ),
        solicitudes_vencidas=Count('id', filter=Q(
            fecha_fin__isnull=False,
            etapa__sla__isnull=False
        ))
    ).order_by('tiempo_promedio')[:10]
    
    rendimiento_usuarios = list(rendimiento_usuarios)
    
    # Procesar datos de rendimiento
    for usuario in rendimiento_usuarios:
        if usuario['tiempo_promedio']:
            horas = usuario['tiempo_promedio'].total_seconds() / 3600
            usuario['horas_promedio'] = round(horas, 2)
            usuario['formato_tiempo'] = f"{int(horas)}h {int((horas % 1) * 60)}m"
        else:
            usuario['horas_promedio'] = 0
            usuario['formato_tiempo'] = '0h 0m'
        
        usuario['full_name'] = f"{usuario['usuario_responsable__first_name'] or ''} {usuario['usuario_responsable__last_name'] or ''}".strip() or usuario['usuario_responsable__username']
    
    # 2. CARGA DE TRABAJO POR USUARIO
    carga_trabajo = Solicitud.objects.filter(
        asignada_a__isnull=False
    ).values(
        'asignada_a__username',
        'asignada_a__first_name',
        'asignada_a__last_name'
    ).annotate(
        total_asignadas=Count('id'),
        solicitudes_activas=Count('id', filter=Q(etapa_actual__isnull=False)),
        solicitudes_urgentes=Count('id', filter=Q(prioridad='Alta')),
        solicitudes_vencidas=Count('id', filter=Q(
            etapa_actual__sla__isnull=False
        ))
    ).order_by('-total_asignadas')[:10]
    
    carga_trabajo = list(carga_trabajo)
    
    for carga in carga_trabajo:
        carga['full_name'] = f"{carga['asignada_a__first_name'] or ''} {carga['asignada_a__last_name'] or ''}".strip() or carga['asignada_a__username']
        carga['porcentaje_vencidas'] = (carga['solicitudes_vencidas'] / carga['total_asignadas'] * 100) if carga['total_asignadas'] > 0 else 0
    
    # 3. EFICIENCIA POR USUARIO
    eficiencia_usuarios = HistorialSolicitud.objects.filter(
        usuario_responsable__isnull=False
    ).values(
        'usuario_responsable__username',
        'usuario_responsable__first_name',
        'usuario_responsable__last_name'
    ).annotate(
        total_transiciones=Count('id'),
        transiciones_completadas=Count('id', filter=Q(fecha_fin__isnull=False)),
        tiempo_promedio=Avg(
            ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        )
    ).order_by('-transiciones_completadas')[:10]
    
    eficiencia_usuarios = list(eficiencia_usuarios)
    
    for eficiencia in eficiencia_usuarios:
        eficiencia['porcentaje_completadas'] = (eficiencia['transiciones_completadas'] / eficiencia['total_transiciones'] * 100) if eficiencia['total_transiciones'] > 0 else 0
        eficiencia['full_name'] = f"{eficiencia['usuario_responsable__first_name'] or ''} {eficiencia['usuario_responsable__last_name'] or ''}".strip() or eficiencia['usuario_responsable__username']
    
    # 4. DATOS PARA GRÁFICAS
    # Gráfica de rendimiento por usuario
    rendimiento_chart_data = {
        'labels': [u['full_name'] for u in rendimiento_usuarios],
        'datasets': [{
            'label': 'Tiempo Promedio (horas)',
            'data': [u['horas_promedio'] for u in rendimiento_usuarios],
            'backgroundColor': 'rgba(54, 162, 235, 0.8)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 2
        }]
    }
    
    # Gráfica de carga de trabajo
    carga_chart_data = {
        'labels': [c['full_name'] for c in carga_trabajo],
        'datasets': [{
            'label': 'Solicitudes Asignadas',
            'data': [c['total_asignadas'] for c in carga_trabajo],
            'backgroundColor': [
                '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1',
                '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#28a745'
            ]
        }]
    }
    
    # Gráfica de eficiencia
    eficiencia_chart_data = {
        'labels': [e['full_name'] for e in eficiencia_usuarios],
        'datasets': [{
            'label': '% Transiciones Completadas',
            'data': [e['porcentaje_completadas'] for e in eficiencia_usuarios],
            'backgroundColor': 'rgba(255, 99, 132, 0.8)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 2
        }]
    }
    
    # Datos para filtros
    pipelines = list(Pipeline.objects.all())
    usuarios = list(User.objects.filter(is_active=True).order_by('username'))
    
    context = {
        'rendimiento_usuarios': rendimiento_usuarios,
        'carga_trabajo': carga_trabajo,
        'eficiencia_usuarios': eficiencia_usuarios,
        'rendimiento_chart_data': rendimiento_chart_data,
        'carga_chart_data': carga_chart_data,
        'eficiencia_chart_data': eficiencia_chart_data,
        'pipelines': pipelines,
        'usuarios': usuarios,
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'pipeline_id': pipeline_id,
            'usuario_id': usuario_id,
        }
    }
    
    return render(request, 'workflow/dashboard_usuario.html', context)


@login_required
def dashboard_cumplimiento(request):
    """
    Dashboard específico para análisis de cumplimiento
    """
    print("DEBUG: Dashboard de cumplimiento llamado")
    
    # Filtros básicos
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    pipeline_id = request.GET.get('pipeline_id', '')
    
    # Base queryset
    queryset = Solicitud.objects.select_related(
        'pipeline', 'etapa_actual', 'subestado_actual'
    )
    
    # Aplicar filtros
    if fecha_inicio:
        queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
    if pipeline_id:
        queryset = queryset.filter(pipeline_id=pipeline_id)
    
    # ==========================================
    # ESTADÍSTICAS DE CUMPLIMIENTO
    # ==========================================
    
    # 1. CUMPLIMIENTO DE SLA POR ETAPA (Cálculo en Python para compatibilidad)
    historiales_completados = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False,
        etapa__sla__isnull=False
    ).select_related('etapa')
    
    # Agrupar por etapa y calcular en Python
    cumplimiento_por_etapa = {}
    for historial in historiales_completados:
        etapa_nombre = historial.etapa.nombre
        if etapa_nombre not in cumplimiento_por_etapa:
            cumplimiento_por_etapa[etapa_nombre] = {
                'etapa__nombre': etapa_nombre,
                'etapa__sla': historial.etapa.sla,
                'total_solicitudes': 0,
                'cumplidas_a_tiempo': 0,
                'tiempo_total': timedelta(0)
            }
        
        cumplimiento_por_etapa[etapa_nombre]['total_solicitudes'] += 1
        
        # Calcular duración
        duracion = historial.fecha_fin - historial.fecha_inicio
        cumplimiento_por_etapa[etapa_nombre]['tiempo_total'] += duracion
        
        # Verificar si cumple SLA
        if duracion <= historial.etapa.sla:
            cumplimiento_por_etapa[etapa_nombre]['cumplidas_a_tiempo'] += 1
    
    # Convertir a lista y calcular promedios
    cumplimiento_sla = []
    for etapa_data in cumplimiento_por_etapa.values():
        total = etapa_data['total_solicitudes']
        cumplidas = etapa_data['cumplidas_a_tiempo']
        
        etapa_data['porcentaje_cumplimiento'] = (cumplidas / total * 100) if total > 0 else 0
        etapa_data['horas_promedio'] = etapa_data['tiempo_total'].total_seconds() / 3600 / total if total > 0 else 0
        
        cumplimiento_sla.append(etapa_data)
    
    # Ordenar por nombre de etapa
    cumplimiento_sla.sort(key=lambda x: x['etapa__nombre'])
    
    # 2. CALIFICACIONES DE COMPLIANCE
    calificaciones_compliance = CalificacionCampo.objects.values(
        'estado'
    ).annotate(
        total=Count('id')
    ).order_by('estado')
    
    calificaciones_compliance = list(calificaciones_compliance)
    
    # 3. REQUISITOS CUMPLIDOS VS PENDIENTES
    requisitos_estado = RequisitoSolicitud.objects.values(
        'cumplido'
    ).annotate(
        total=Count('id')
    ).order_by('cumplido')
    
    requisitos_estado = list(requisitos_estado)
    
    # 4. DATOS PARA GRÁFICAS
    # Gráfica de cumplimiento SLA
    cumplimiento_chart_data = {
        'labels': [c['etapa__nombre'] for c in cumplimiento_sla],
        'datasets': [{
            'label': '% Cumplimiento SLA',
            'data': [c['porcentaje_cumplimiento'] for c in cumplimiento_sla],
            'backgroundColor': 'rgba(75, 192, 192, 0.8)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 2
        }]
    }
    
    # Gráfica de calificaciones
    calificaciones_chart_data = {
        'labels': [c['estado'].title() for c in calificaciones_compliance],
        'datasets': [{
            'label': 'Cantidad',
            'data': [c['total'] for c in calificaciones_compliance],
            'backgroundColor': [
                '#28a745', '#ffc107', '#dc3545'
            ]
        }]
    }
    
    # Gráfica de requisitos
    requisitos_chart_data = {
        'labels': ['Cumplidos', 'Pendientes'],
        'datasets': [{
            'label': 'Requisitos',
            'data': [
                sum(1 for r in requisitos_estado if r['cumplido']),
                sum(1 for r in requisitos_estado if not r['cumplido'])
            ],
            'backgroundColor': ['#28a745', '#dc3545']
        }]
    }
    
    # Datos para filtros
    pipelines = list(Pipeline.objects.all())
    
    context = {
        'cumplimiento_sla': cumplimiento_sla,
        'calificaciones_compliance': calificaciones_compliance,
        'requisitos_estado': requisitos_estado,
        'cumplimiento_chart_data': cumplimiento_chart_data,
        'calificaciones_chart_data': calificaciones_chart_data,
        'requisitos_chart_data': requisitos_chart_data,
        'pipelines': pipelines,
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'pipeline_id': pipeline_id,
        }
    }
    
    return render(request, 'workflow/dashboard_cumplimiento.html', context)


@login_required
def dashboard_flujo(request):
    """
    Dashboard específico para análisis de flujo
    """
    print("DEBUG: Dashboard de flujo llamado")
    
    # Filtros básicos
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    pipeline_id = request.GET.get('pipeline_id', '')
    
    # Base queryset
    queryset = Solicitud.objects.select_related(
        'pipeline', 'etapa_actual', 'subestado_actual'
    )
    
    # Aplicar filtros
    if fecha_inicio:
        queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
    if pipeline_id:
        queryset = queryset.filter(pipeline_id=pipeline_id)
    
    # ==========================================
    # ESTADÍSTICAS DE FLUJO
    # ==========================================
    
    # 1. FLUJO POR ETAPA
    flujo_etapas = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).values(
        'etapa__nombre',
        'etapa__pipeline__nombre'
    ).annotate(
        total_solicitudes=Count('id'),
        tiempo_promedio=Avg(
            ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        ),
        solicitudes_vencidas=Count('id', filter=Q(
            fecha_fin__isnull=False,
            etapa__sla__isnull=False
        ))
    ).order_by('etapa__pipeline__nombre', 'etapa__nombre')
    
    flujo_etapas = list(flujo_etapas)
    
    for flujo in flujo_etapas:
        if flujo['tiempo_promedio']:
            flujo['horas_promedio'] = flujo['tiempo_promedio'].total_seconds() / 3600
        else:
            flujo['horas_promedio'] = 0
        flujo['porcentaje_vencidas'] = (flujo['solicitudes_vencidas'] / flujo['total_solicitudes'] * 100) if flujo['total_solicitudes'] > 0 else 0
    
    # 2. TRANSICIONES MÁS FRECUENTES
    transiciones_frecuentes = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).values(
        'etapa__nombre',
        'solicitud__pipeline__nombre'
    ).annotate(
        total_transiciones=Count('id'),
        tiempo_promedio=Avg(
            ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        )
    ).order_by('-total_transiciones')[:10]
    
    transiciones_frecuentes = list(transiciones_frecuentes)
    
    for transicion in transiciones_frecuentes:
        if transicion['tiempo_promedio']:
            transicion['horas_promedio'] = transicion['tiempo_promedio'].total_seconds() / 3600
        else:
            transicion['horas_promedio'] = 0
    
    # 3. CUELLOS DE BOTELLA
    cuellos_botella = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False,
        etapa__sla__isnull=False
    ).values(
        'etapa__nombre',
        'etapa__pipeline__nombre'
    ).annotate(
        total_solicitudes=Count('id'),
        promedio_horas=Avg(
            ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        ),
        sla_horas=F('etapa__sla')
    ).filter(
        promedio_horas__gt=F('etapa__sla')
    ).order_by('-promedio_horas')[:10]
    
    cuellos_botella = list(cuellos_botella)
    
    for cuello in cuellos_botella:
        if cuello['promedio_horas']:
            cuello['horas_promedio'] = cuello['promedio_horas'].total_seconds() / 3600
        else:
            cuello['horas_promedio'] = 0
        if cuello['sla_horas']:
            cuello['sla_horas_valor'] = cuello['sla_horas'].total_seconds() / 3600
        else:
            cuello['sla_horas_valor'] = 0
    
    # 4. DATOS PARA GRÁFICAS
    # Gráfica de flujo por etapa
    flujo_chart_data = {
        'labels': [f['etapa__nombre'] for f in flujo_etapas],
        'datasets': [{
            'label': 'Tiempo Promedio (horas)',
            'data': [f['horas_promedio'] for f in flujo_etapas],
            'backgroundColor': 'rgba(153, 102, 255, 0.8)',
            'borderColor': 'rgba(153, 102, 255, 1)',
            'borderWidth': 2
        }]
    }
    
    # Gráfica de transiciones
    transiciones_chart_data = {
        'labels': [t['etapa__nombre'] for t in transiciones_frecuentes],
        'datasets': [{
            'label': 'Total Transiciones',
            'data': [t['total_transiciones'] for t in transiciones_frecuentes],
            'backgroundColor': [
                '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1',
                '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#28a745'
            ]
        }]
    }
    
    # Gráfica de cuellos de botella
    cuellos_chart_data = {
        'labels': [c['etapa__nombre'] for c in cuellos_botella],
        'datasets': [
            {
                'label': 'Tiempo Promedio (horas)',
                'data': [c['horas_promedio'] for c in cuellos_botella],
                'backgroundColor': 'rgba(255, 99, 132, 0.8)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 2
            },
            {
                'label': 'SLA (horas)',
                'data': [c['sla_horas_valor'] for c in cuellos_botella],
                'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2
            }
        ]
    }
    
    # Datos para filtros
    pipelines = list(Pipeline.objects.all())
    
    context = {
        'flujo_etapas': flujo_etapas,
        'transiciones_frecuentes': transiciones_frecuentes,
        'cuellos_botella': cuellos_botella,
        'flujo_chart_data': flujo_chart_data,
        'transiciones_chart_data': transiciones_chart_data,
        'cuellos_chart_data': cuellos_chart_data,
        'pipelines': pipelines,
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'pipeline_id': pipeline_id,
        }
    }
    
    return render(request, 'workflow/dashboard_flujo.html', context)


@login_required
def dashboard_comite(request):
    """
    Dashboard específico para análisis de comité
    """
    print("DEBUG: Dashboard de comité llamado")
    
    # Filtros básicos
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    nivel_id = request.GET.get('nivel_id', '')
    
    # Base queryset
    queryset = Solicitud.objects.select_related(
        'pipeline', 'etapa_actual', 'subestado_actual'
    )
    
    # Aplicar filtros
    if fecha_inicio:
        queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
    
    # ==========================================
    # ESTADÍSTICAS DE COMITÉ
    # ==========================================
    
    # 1. PARTICIPACIÓN POR NIVEL
    participacion_niveles = ParticipacionComite.objects.values(
        'nivel__nombre',
        'resultado'
    ).annotate(
        total_participaciones=Count('id')
    ).order_by('nivel__nombre', 'resultado')
    
    participacion_niveles = list(participacion_niveles)
    
    # 2. RESULTADOS POR USUARIO
    resultados_usuarios = ParticipacionComite.objects.values(
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'resultado'
    ).annotate(
        total_participaciones=Count('id')
    ).order_by('-total_participaciones')[:10]
    
    resultados_usuarios = list(resultados_usuarios)
    
    for resultado in resultados_usuarios:
        resultado['full_name'] = f"{resultado['usuario__first_name'] or ''} {resultado['usuario__last_name'] or ''}".strip() or resultado['usuario__username']
    
    # 3. ESCALAMIENTOS POR NIVEL
    escalamientos_niveles = SolicitudEscalamientoComite.objects.values(
        'nivel_solicitado__nombre'
    ).annotate(
        total_escalamientos=Count('id'),
        atendidos=Count('id', filter=Q(atendido=True)),
        no_atendidos=Count('id', filter=Q(atendido=False))
    ).order_by('-total_escalamientos')
    
    escalamientos_niveles = list(escalamientos_niveles)
    
    for escalamiento in escalamientos_niveles:
        escalamiento['porcentaje_atendidos'] = (escalamiento['atendidos'] / escalamiento['total_escalamientos'] * 100) if escalamiento['total_escalamientos'] > 0 else 0
    
    # 4. TIEMPO DE RESPUESTA DEL COMITÉ
    tiempo_respuesta = ParticipacionComite.objects.filter(
        fecha_modificacion__isnull=False
    ).values(
        'nivel__nombre'
    ).annotate(
        tiempo_promedio=Avg(
            ExpressionWrapper(
                F('fecha_modificacion') - F('fecha_creacion'),
                output_field=fields.DurationField()
            )
        )
    ).order_by('nivel__nombre')
    
    tiempo_respuesta = list(tiempo_respuesta)
    
    for tiempo in tiempo_respuesta:
        if tiempo['tiempo_promedio']:
            tiempo['horas_promedio'] = tiempo['tiempo_promedio'].total_seconds() / 3600
        else:
            tiempo['horas_promedio'] = 0
    
    # 5. DATOS PARA GRÁFICAS
    # Gráfica de participación por nivel
    participacion_chart_data = {
        'labels': [p['nivel__nombre'] for p in participacion_niveles],
        'datasets': [{
            'label': 'Total Participaciones',
            'data': [p['total_participaciones'] for p in participacion_niveles],
            'backgroundColor': [
                '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1'
            ]
        }]
    }
    
    # Gráfica de resultados por usuario
    resultados_chart_data = {
        'labels': [r['full_name'] for r in resultados_usuarios],
        'datasets': [{
            'label': 'Total Participaciones',
            'data': [r['total_participaciones'] for r in resultados_usuarios],
            'backgroundColor': 'rgba(75, 192, 192, 0.8)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 2
        }]
    }
    
    # Gráfica de escalamientos
    escalamientos_chart_data = {
        'labels': [e['nivel_solicitado__nombre'] for e in escalamientos_niveles],
        'datasets': [
            {
                'label': 'Atendidos',
                'data': [e['atendidos'] for e in escalamientos_niveles],
                'backgroundColor': 'rgba(75, 192, 192, 0.8)'
            },
            {
                'label': 'No Atendidos',
                'data': [e['no_atendidos'] for e in escalamientos_niveles],
                'backgroundColor': 'rgba(255, 99, 132, 0.8)'
            }
        ]
    }
    
    # Datos para filtros
    niveles = list(NivelComite.objects.all().order_by('orden'))
    
    context = {
        'participacion_niveles': participacion_niveles,
        'resultados_usuarios': resultados_usuarios,
        'escalamientos_niveles': escalamientos_niveles,
        'tiempo_respuesta': tiempo_respuesta,
        'participacion_chart_data': participacion_chart_data,
        'resultados_chart_data': resultados_chart_data,
        'escalamientos_chart_data': escalamientos_chart_data,
        'niveles': niveles,
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'nivel_id': nivel_id,
        }
    }
    
    return render(request, 'workflow/dashboard_comite.html', context)


# ==========================================
# ROUTER DASHBOARD PRINCIPAL
# ==========================================

@login_required
def dashboard_router(request):
    """
    Dashboard principal que redirige según el rol del usuario
    """
    user = request.user
    
    # Superuser puede elegir el dashboard
    if user.is_superuser:
        dashboard_type = request.GET.get('type', 'operativo')
        
        if dashboard_type == 'negocios':
            return dashboard_negocios(request)
        elif dashboard_type == 'comite':
            return dashboard_comite(request)
        elif dashboard_type == 'bandeja':
            return dashboard_bandeja_trabajo(request)
        else:
            return dashboard_operativo(request)
    
    # Verificar si es Oficial de Negocio o miembro del grupo NEGOCIOS
    if user.groups.filter(name='Oficial de Negocio').exists() or user.groups.filter(name='NEGOCIOS').exists():
        return dashboard_negocios(request)
    
    # Verificar si es miembro del Comité de Crédito
    if user.groups.filter(name__icontains='Comité').exists() or user.groups.filter(name__icontains='Comite').exists():
        return dashboard_comite(request)
    
    # Verificar si tiene acceso a bandejas grupales
    bandeja_permisos = PermisoBandeja.objects.filter(
        Q(usuario=user) | Q(grupo__in=user.groups.all()),
        etapa__es_bandeja_grupal=True,
        puede_ver=True
    ).exists()
    
    if bandeja_permisos:
        return dashboard_bandeja_trabajo(request)
    
    # Por defecto, dashboard operativo
    return dashboard_operativo(request)


# ==========================================
# DASHBOARD DE NEGOCIOS
# ==========================================

@login_required
def dashboard_negocios(request):
    """
    Dashboard específico para Oficiales de Negocio
    """
    user = request.user
    
    # Verificar permisos (excepto superuser)
    if not user.is_superuser and not (user.groups.filter(name='Oficial de Negocio').exists() or user.groups.filter(name='NEGOCIOS').exists()):
        # Redirigir al dashboard apropiado
        return dashboard_router(request)
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Base queryset - solicitudes creadas por el usuario
    queryset_solicitudes = Solicitud.objects.filter(
        creada_por=user
    ).select_related('pipeline', 'etapa_actual', 'cliente', 'cotizacion')
    
    # Base queryset - cotizaciones creadas por el usuario
    queryset_cotizaciones = Cotizacion.objects.filter(
        added_by=user
    ).select_related('cliente')
    
    # Aplicar filtros de fecha
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            queryset_solicitudes = queryset_solicitudes.filter(fecha_creacion__gte=fecha_inicio_dt)
            queryset_cotizaciones = queryset_cotizaciones.filter(created_at__gte=fecha_inicio_dt)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            queryset_solicitudes = queryset_solicitudes.filter(fecha_creacion__lte=fecha_fin_dt)
            queryset_cotizaciones = queryset_cotizaciones.filter(created_at__lte=fecha_fin_dt)
        except ValueError:
            pass
    
    # ==========================================
    # KPIs PRINCIPALES - SOLICITUDES
    # ==========================================
    
    total_solicitudes = queryset_solicitudes.count()
    solicitudes_activas = queryset_solicitudes.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = queryset_solicitudes.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por etapa
    solicitudes_por_etapa = queryset_solicitudes.filter(
        etapa_actual__isnull=False
    ).values(
        'etapa_actual__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    # ==========================================
    # KPIs PRINCIPALES - COTIZACIONES
    # ==========================================
    
    total_cotizaciones = queryset_cotizaciones.count()
    cotizaciones_activas = total_cotizaciones  # All user's cotizaciones are considered active
    cotizaciones_por_estado = []  # No estado field available in Cotizacion model
    
    # ==========================================
    # NOTAS Y RECORDATORIOS
    # ==========================================
    
    # Obtener notas y recordatorios de las solicitudes del usuario
    notas_recordatorios = NotaRecordatorio.objects.filter(
        solicitud__creada_por=user,
        fecha_vencimiento__gte=timezone.now()
    ).select_related('solicitud').order_by('fecha_vencimiento')[:10]
    
    # ==========================================
    # RENDIMIENTO TEMPORAL
    # ==========================================
    
    # Solicitudes creadas por mes en los últimos 6 meses
    hace_6_meses = timezone.now() - timedelta(days=180)
    solicitudes_por_mes = queryset_solicitudes.filter(
        fecha_creacion__gte=hace_6_meses
    ).extra(
        select={'mes': "strftime('%%Y-%%m', fecha_creacion)"}
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')
    
    # Cotizaciones creadas por mes
    cotizaciones_por_mes = queryset_cotizaciones.filter(
        created_at__gte=hace_6_meses
    ).extra(
        select={'mes': "strftime('%%Y-%%m', created_at)"}
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')
    
    # ==========================================
    # HISTORIAL DE RENDIMIENTO
    # ==========================================
    
    # Tiempo promedio en completar solicitudes
    historiales_completados = HistorialSolicitud.objects.filter(
        solicitud__creada_por=user,
        fecha_fin__isnull=False
    ).select_related('solicitud')
    
    tiempo_promedio_completion = 0
    if historiales_completados.exists():
        total_duracion = timedelta()
        count = 0
        for historial in historiales_completados:
            if historial.fecha_fin and historial.fecha_inicio:
                total_duracion += historial.fecha_fin - historial.fecha_inicio
                count += 1
        
        if count > 0:
            tiempo_promedio_completion = total_duracion.total_seconds() / (count * 24 * 3600)  # En días
    
    context = {
        'dashboard_type': 'negocios',
        'user_name': user.get_full_name() or user.username,
        
        # KPIs Solicitudes
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_por_etapa': list(solicitudes_por_etapa),
        
        # KPIs Cotizaciones
        'total_cotizaciones': total_cotizaciones,
        'cotizaciones_activas': cotizaciones_activas,
        'cotizaciones_por_estado': list(cotizaciones_por_estado),
        
        # Notas y recordatorios
        'notas_recordatorios': notas_recordatorios,
        
        # Rendimiento temporal
        'solicitudes_por_mes': list(solicitudes_por_mes),
        'cotizaciones_por_mes': list(cotizaciones_por_mes),
        'tiempo_promedio_completion': round(tiempo_promedio_completion, 2),
        
        # Filtros
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
    }
    
    return render(request, 'workflow/dashboard_negocios.html', context)


# ==========================================
# DASHBOARD DE BANDEJA DE TRABAJO
# ==========================================

@login_required
def dashboard_bandeja_trabajo(request):
    """
    Dashboard para usuarios con acceso a bandejas grupales
    """
    user = request.user
    
    # Obtener etapas a las que el usuario tiene acceso
    if user.is_superuser:
        etapas_acceso = Etapa.objects.filter(es_bandeja_grupal=True)
    else:
        etapas_acceso = Etapa.objects.filter(
            Q(permisos_bandeja__usuario=user) | Q(permisos_bandeja__grupo__in=user.groups.all()),
            es_bandeja_grupal=True,
            permisos_bandeja__puede_ver=True
        ).distinct()
    
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    etapa_id = request.GET.get('etapa_id')
    
    # Queryset base - solicitudes en las etapas accesibles
    queryset = Solicitud.objects.filter(
        etapa_actual__in=etapas_acceso
    ).select_related('pipeline', 'etapa_actual', 'creada_por', 'asignada_a')
    
    # Aplicar filtros
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio_dt)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin_dt)
        except ValueError:
            pass
    
    if etapa_id:
        queryset = queryset.filter(etapa_actual_id=etapa_id)
    
    # ==========================================
    # KPIs PRINCIPALES
    # ==========================================
    
    total_solicitudes_bandeja = queryset.count()
    solicitudes_sin_asignar = queryset.filter(asignada_a__isnull=True).count()
    solicitudes_asignadas = queryset.filter(asignada_a__isnull=False).count()
    
    # Solicitudes vencidas (cálculo en Python)
    solicitudes_vencidas = 0
    for solicitud in queryset:
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            tiempo_actual = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_actual > solicitud.etapa_actual.sla:
                solicitudes_vencidas += 1
    
    # ==========================================
    # DISTRIBUCIÓN POR ETAPA
    # ==========================================
    
    solicitudes_por_etapa = {}
    for solicitud in queryset:
        etapa_nombre = solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin Etapa'
        if etapa_nombre not in solicitudes_por_etapa:
            solicitudes_por_etapa[etapa_nombre] = {
                'total': 0,
                'sin_asignar': 0,
                'vencidas': 0
            }
        
        solicitudes_por_etapa[etapa_nombre]['total'] += 1
        if not solicitud.asignada_a:
            solicitudes_por_etapa[etapa_nombre]['sin_asignar'] += 1
        
        # Verificar si está vencida
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            tiempo_actual = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_actual > solicitud.etapa_actual.sla:
                solicitudes_por_etapa[etapa_nombre]['vencidas'] += 1
    
    # Convertir a lista para el template
    solicitudes_por_etapa_list = [
        {
            'etapa': etapa,
            'total': data['total'],
            'sin_asignar': data['sin_asignar'],
            'vencidas': data['vencidas']
        }
        for etapa, data in solicitudes_por_etapa.items()
    ]
    
    # ==========================================
    # PRODUCTIVIDAD DEL EQUIPO
    # ==========================================
    
    # Solicitudes procesadas en las etapas (historial)
    hace_30_dias = timezone.now() - timedelta(days=30)
    solicitudes_procesadas = HistorialSolicitud.objects.filter(
        etapa__in=etapas_acceso,
        fecha_fin__gte=hace_30_dias,
        fecha_fin__isnull=False
    ).count()
    
    # Tiempo promedio de procesamiento por etapa
    promedios_por_etapa = []
    for etapa in etapas_acceso:
        historiales = HistorialSolicitud.objects.filter(
            etapa=etapa,
            fecha_fin__isnull=False,
            fecha_fin__gte=hace_30_dias
        )
        
        if historiales.exists():
            total_duracion = timedelta()
            count = 0
            for historial in historiales:
                if historial.fecha_fin and historial.fecha_inicio:
                    total_duracion += historial.fecha_fin - historial.fecha_inicio
                    count += 1
            
            if count > 0:
                promedio_horas = total_duracion.total_seconds() / (count * 3600)
                promedios_por_etapa.append({
                    'etapa': etapa.nombre,
                    'promedio_horas': round(promedio_horas, 2),
                    'casos_procesados': count
                })
    
    # ==========================================
    # USUARIOS MÁS ACTIVOS EN LAS BANDEJAS
    # ==========================================
    
    usuarios_activos = queryset.filter(
        asignada_a__isnull=False
    ).values(
        'asignada_a__username',
        'asignada_a__first_name',
        'asignada_a__last_name'
    ).annotate(
        total_asignadas=Count('id')
    ).order_by('-total_asignadas')[:10]
    
    # Convertir a lista y agregar nombres completos
    usuarios_activos_list = []
    for usuario_data in usuarios_activos:
        usuario_data['full_name'] = f"{usuario_data['asignada_a__first_name'] or ''} {usuario_data['asignada_a__last_name'] or ''}".strip() or usuario_data['asignada_a__username']
        usuarios_activos_list.append(usuario_data)
    
    context = {
        'dashboard_type': 'bandeja',
        'etapas_acceso': etapas_acceso,
        
        # KPIs principales
        'total_solicitudes_bandeja': total_solicitudes_bandeja,
        'solicitudes_sin_asignar': solicitudes_sin_asignar,
        'solicitudes_asignadas': solicitudes_asignadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        
        # Distribución
        'solicitudes_por_etapa': solicitudes_por_etapa_list,
        
        # Productividad
        'solicitudes_procesadas_30_dias': solicitudes_procesadas,
        'promedios_por_etapa': promedios_por_etapa,
        'usuarios_activos': usuarios_activos_list,
        
        # Filtros
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'etapa_id': etapa_id,
        },
        'etapas_disponibles': etapas_acceso,
    }
    
    return render(request, 'workflow/dashboard_bandeja.html', context)


# ==========================================
# DASHBOARD DE COMITÉ (ENHANCED)
# ==========================================

@login_required
def dashboard_comite_enhanced(request):
    """
    Dashboard mejorado específico para miembros del Comité de Crédito
    """
    user = request.user
    
    # Verificar permisos
    if not user.is_superuser and not (user.groups.filter(name__icontains='Comité').exists() or user.groups.filter(name__icontains='Comite').exists()):
        return dashboard_router(request)
    
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    nivel_id = request.GET.get('nivel_id')
    
    # Base queryset - solicitudes escaladas al comité
    queryset = SolicitudEscalamientoComite.objects.select_related(
        'solicitud', 'nivel_comite', 'usuario_escalamiento'
    )
    
    # Aplicar filtros
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            queryset = queryset.filter(fecha_escalamiento__gte=fecha_inicio_dt)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            queryset = queryset.filter(fecha_escalamiento__lte=fecha_fin_dt)
        except ValueError:
            pass
    
    if nivel_id:
        queryset = queryset.filter(nivel_comite_id=nivel_id)
    
    # ==========================================
    # KPIs PRINCIPALES DEL COMITÉ
    # ==========================================
    
    total_escalamientos = queryset.count()
    escalamientos_pendientes = queryset.filter(
        resultado__isnull=True,
        fecha_resolucion__isnull=True
    ).count()
    escalamientos_aprobados = queryset.filter(resultado='aprobado').count()
    escalamientos_rechazados = queryset.filter(resultado='rechazado').count()
    
    # ==========================================
    # PARTICIPACIÓN DEL USUARIO ACTUAL
    # ==========================================
    
    if not user.is_superuser:
        # Participaciones del usuario actual
        participaciones_usuario = ParticipacionComite.objects.filter(
            usuario=user
        ).select_related('escalamiento', 'escalamiento__solicitud')
        
        participaciones_pendientes = participaciones_usuario.filter(
            voto__isnull=True
        ).count()
        
        participaciones_completadas = participaciones_usuario.filter(
            voto__isnull=False
        ).count()
    else:
        # Para superuser, mostrar estadísticas generales
        participaciones_pendientes = ParticipacionComite.objects.filter(
            voto__isnull=True
        ).count()
        participaciones_completadas = ParticipacionComite.objects.filter(
            voto__isnull=False
        ).count()
    
    # ==========================================
    # TIEMPO DE RESPUESTA DEL COMITÉ
    # ==========================================
    
    escalamientos_resueltos = queryset.filter(
        fecha_resolucion__isnull=False
    )
    
    tiempo_promedio_resolucion = 0
    if escalamientos_resueltos.exists():
        total_duracion = timedelta()
        count = 0
        for escalamiento in escalamientos_resueltos:
            if escalamiento.fecha_resolucion and escalamiento.fecha_escalamiento:
                total_duracion += escalamiento.fecha_resolucion - escalamiento.fecha_escalamiento
                count += 1
        
        if count > 0:
            tiempo_promedio_resolucion = total_duracion.total_seconds() / (count * 24 * 3600)  # En días
    
    # ==========================================
    # DISTRIBUCIÓN POR NIVEL
    # ==========================================
    
    escalamientos_por_nivel = queryset.values(
        'nivel_comite__nombre',
        'nivel_comite__orden'
    ).annotate(
        total=Count('id'),
        pendientes=Count('id', filter=Q(resultado__isnull=True)),
        aprobados=Count('id', filter=Q(resultado='aprobado')),
        rechazados=Count('id', filter=Q(resultado='rechazado'))
    ).order_by('nivel_comite__orden')
    
    context = {
        'dashboard_type': 'comite',
        'user_name': user.get_full_name() or user.username,
        
        # KPIs principales
        'total_escalamientos': total_escalamientos,
        'escalamientos_pendientes': escalamientos_pendientes,
        'escalamientos_aprobados': escalamientos_aprobados,
        'escalamientos_rechazados': escalamientos_rechazados,
        
        # Participación del usuario
        'participaciones_pendientes': participaciones_pendientes,
        'participaciones_completadas': participaciones_completadas,
        
        # Tiempos
        'tiempo_promedio_resolucion': round(tiempo_promedio_resolucion, 2),
        
        # Distribución
        'escalamientos_por_nivel': list(escalamientos_por_nivel),
        
        # Filtros
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'nivel_id': nivel_id,
        },
        'niveles_disponibles': NivelComite.objects.all().order_by('orden'),
    }
    
    return render(request, 'workflow/dashboard_comite_enhanced.html', context)
    
    return render(request, 'workflow/dashboard_comite.html', context) 