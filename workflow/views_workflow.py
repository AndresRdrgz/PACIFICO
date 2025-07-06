from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth.models import Group
from .modelsWorkflow import *
from .models import ClienteEntrevista
import json
from datetime import datetime, timedelta

# ==========================================
# VISTAS PRINCIPALES DEL WORKFLOW
# ==========================================

@login_required
def dashboard_workflow(request):
    """Dashboard principal del sistema de workflow"""
    
    # Obtener solicitudes del usuario
    solicitudes_asignadas = Solicitud.objects.filter(
        asignada_a=request.user
    ).select_related('tipo_solicitud', 'pipeline', 'etapa_actual', 'subestado_actual')
    
    # Obtener bandejas grupales a las que tiene acceso
    grupos_usuario = request.user.groups.all()
    etapas_grupales = Etapa.objects.filter(
        es_bandeja_grupal=True,
        permisos__grupo__in=grupos_usuario,
        permisos__puede_ver=True
    )
    
    solicitudes_grupales = Solicitud.objects.filter(
        etapa_actual__in=etapas_grupales,
        asignada_a__isnull=True
    ).select_related('tipo_solicitud', 'pipeline', 'etapa_actual', 'subestado_actual')
    
    # Estadísticas
    total_solicitudes = solicitudes_asignadas.count() + solicitudes_grupales.count()
    solicitudes_vencidas = 0
    solicitudes_proximo_vencer = 0
    
    for solicitud in solicitudes_asignadas:
        if solicitud.etapa_actual:
            tiempo_en_etapa = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_en_etapa > solicitud.etapa_actual.sla:
                solicitudes_vencidas += 1
            elif tiempo_en_etapa > solicitud.etapa_actual.sla * 0.8:  # 80% del SLA
                solicitudes_proximo_vencer += 1
    
    # Pipelines disponibles
    pipelines = Pipeline.objects.all()
    
    context = {
        'solicitudes_asignadas': solicitudes_asignadas[:10],
        'solicitudes_grupales': solicitudes_grupales[:10],
        'total_solicitudes': total_solicitudes,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_proximo_vencer': solicitudes_proximo_vencer,
        'pipelines': pipelines,
        'etapas_grupales': etapas_grupales,
    }
    
    return render(request, 'workflow/dashboard.html', context)


@login_required
def negocios_view(request):
    """Vista de Negocios - Ver todas las solicitudes de un pipeline"""
    
    # Obtener pipeline seleccionado
    pipeline_id = request.GET.get('pipeline')
    view_type = request.GET.get('view', 'table')  # table or kanban
    
    # Obtener todos los pipelines disponibles
    pipelines = Pipeline.objects.all()
    
    if pipeline_id:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Obtener todas las solicitudes del pipeline
        solicitudes = Solicitud.objects.filter(
            pipeline=pipeline
        ).select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
        # Filtros básicos
        filtro_estado = request.GET.get('estado', '')
        filtro_asignado = request.GET.get('asignado', '')
        filtro_fecha = request.GET.get('fecha', '')
        
        # Nuevos filtros avanzados
        busqueda = request.GET.get('busqueda', '')
        filtro_sla = request.GET.get('sla', '')
        ordenar_por = request.GET.get('ordenar', 'fecha_creacion')
        
        # Aplicar filtros
        if filtro_estado == 'activas':
            solicitudes = solicitudes.filter(etapa_actual__isnull=False)
        elif filtro_estado == 'completadas':
            solicitudes = solicitudes.filter(etapa_actual__isnull=True)
        elif filtro_estado == 'vencidas':
            solicitudes = solicitudes.filter(
                etapa_actual__isnull=False,
                fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
            )
        
        if filtro_asignado == 'asignadas':
            solicitudes = solicitudes.filter(asignada_a__isnull=False)
        elif filtro_asignado == 'sin_asignar':
            solicitudes = solicitudes.filter(asignada_a__isnull=True)
        
        if filtro_fecha == 'hoy':
            solicitudes = solicitudes.filter(fecha_creacion__date=timezone.now().date())
        elif filtro_fecha == 'semana':
            solicitudes = solicitudes.filter(
                fecha_creacion__gte=timezone.now() - timedelta(days=7)
            )
        elif filtro_fecha == 'mes':
            solicitudes = solicitudes.filter(
                fecha_creacion__gte=timezone.now() - timedelta(days=30)
            )
        
        # Filtro de búsqueda
        if busqueda:
            solicitudes = solicitudes.filter(
                Q(codigo__icontains=busqueda) |
                Q(creada_por__first_name__icontains=busqueda) |
                Q(creada_por__last_name__icontains=busqueda) |
                Q(creada_por__username__icontains=busqueda) |
                Q(asignada_a__first_name__icontains=busqueda) |
                Q(asignada_a__last_name__icontains=busqueda) |
                Q(asignada_a__username__icontains=busqueda)
            )
        
        # Filtro de SLA
        if filtro_sla == 'vencido':
            solicitudes = solicitudes.filter(
                etapa_actual__isnull=False,
                fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
            )
        elif filtro_sla == 'proximo':
            # Solicitudes próximas a vencer (80% del SLA)
            solicitudes = solicitudes.filter(
                etapa_actual__isnull=False,
                fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla') * 0.8,
                fecha_ultima_actualizacion__gte=timezone.now() - F('etapa_actual__sla')
            )
        elif filtro_sla == 'ok':
            solicitudes = solicitudes.filter(
                etapa_actual__isnull=False,
                fecha_ultima_actualizacion__gte=timezone.now() - F('etapa_actual__sla') * 0.8
            )
        
        # Ordenamiento
        if ordenar_por == 'fecha_creacion':
            solicitudes = solicitudes.order_by('-fecha_creacion')
        elif ordenar_por == 'fecha_ultima_actualizacion':
            solicitudes = solicitudes.order_by('-fecha_ultima_actualizacion')
        elif ordenar_por == 'codigo':
            solicitudes = solicitudes.order_by('codigo')
        elif ordenar_por == 'etapa':
            solicitudes = solicitudes.order_by('etapa_actual__orden')
        else:
            solicitudes = solicitudes.order_by('-fecha_creacion')
        
        # Paginación
        paginator = Paginator(solicitudes, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # --- ENRIQUECER DATOS PARA LA TABLA ---
        solicitudes_tabla = []
        now = timezone.now()
        ETAPA_COLORS = [
            'bg-primary', 'bg-info', 'bg-warning', 'bg-success', 'bg-danger', 'bg-secondary', 'bg-dark'
        ]
        etapas_pipeline = list(pipeline.etapas.order_by('orden').values_list('nombre', flat=True))
        etapa_color_map = {nombre: ETAPA_COLORS[i % len(ETAPA_COLORS)] for i, nombre in enumerate(etapas_pipeline)}

        for solicitud in page_obj:
            # Campos personalizados
            valores = {v.campo.nombre.lower(): v for v in solicitud.valores_personalizados.select_related('campo').all()}
            get_valor = lambda nombre: valores.get(nombre.lower()).valor() if valores.get(nombre.lower()) else None

            # Cliente y cédula
            cliente = get_valor('cliente') or (solicitud.creada_por.get_full_name() or solicitud.creada_por.username)
            cedula = get_valor('cédula') or get_valor('cedula') or ''
            producto = get_valor('producto') or ''
            monto = get_valor('monto solicitado') or get_valor('monto') or 0
            try:
                monto_float = float(monto)
            except:
                monto_float = 0
            monto_formateado = "$ {:,.0f}".format(monto_float)

            # Fechas
            fecha_inicio = solicitud.fecha_creacion
            sla = solicitud.etapa_actual.sla if solicitud.etapa_actual else None
            vencimiento_sla = fecha_inicio + sla if sla else None
            fecha_vencimiento_str = vencimiento_sla.strftime('%d/%m/%Y') if vencimiento_sla else 'N/A'

            # SLA restante mejorado con semáforo visual
            if sla and solicitud.etapa_actual:
                tiempo_total = sla.total_seconds()
                tiempo_restante = (fecha_inicio + sla) - now
                segundos_restantes = tiempo_restante.total_seconds()
                porcentaje_restante = (segundos_restantes / tiempo_total) * 100 if tiempo_total > 0 else 0
                abs_segundos = abs(int(segundos_restantes))
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                if segundos_restantes < 0:
                    if horas > 0:
                        sla_restante = f"-{horas}h {minutos}m"
                    else:
                        sla_restante = f"-{minutos}m"
                    sla_color = 'text-danger'
                elif porcentaje_restante > 40:
                    if horas > 0:
                        sla_restante = f"{horas}h {minutos}m"
                    else:
                        sla_restante = f"{minutos}m"
                    sla_color = 'text-success'
                elif porcentaje_restante > 0:
                    if horas > 0:
                        sla_restante = f"{horas}h {minutos}m"
                    else:
                        sla_restante = f"{minutos}m"
                    sla_color = 'text-warning'
                else:
                    if horas > 0:
                        sla_restante = f"-{horas}h {minutos}m"
                    else:
                        sla_restante = f"-{minutos}m"
                    sla_color = 'text-danger'
            else:
                sla_restante = 'N/A'
                sla_color = 'text-secondary'

            # Alertas automáticas
            alertas = []
            if sla_color == 'text-danger':
                alertas.append({'icon': 'fa-exclamation-triangle', 'color': 'danger', 'tooltip': 'SLA vencido'})
            elif sla_color == 'text-warning':
                alertas.append({'icon': 'fa-exclamation-circle', 'color': 'warning', 'tooltip': 'SLA por vencer'})
            else:
                alertas.append({'icon': 'fa-check-circle', 'color': 'success', 'tooltip': 'SLA en tiempo'})

            # Estado actual
            estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            estado_color = 'primary' if estado_actual == 'En Proceso' else 'success' if estado_actual == 'Completado' else 'secondary'

            # Acciones (estructura lista para condicionar por etapa)
            acciones = {
                'ver': True,
                'cambiar_etapa': True,
                'exportar': True,
                'eliminar': True,
            }

            etapa_nombre = solicitud.etapa_actual.nombre if solicitud.etapa_actual else ''
            etapa_color = etapa_color_map.get(etapa_nombre, 'bg-secondary')

            solicitudes_tabla.append({
                'codigo': solicitud.codigo,
                'cliente': cliente,
                'cedula': cedula,
                'producto': producto,
                'monto': monto_formateado,
                'propietario': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
                'asignado_a': (solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username) if solicitud.asignada_a else 'Sin asignar',
                'etapa': solicitud.etapa_actual.nombre if solicitud.etapa_actual else '',
                'estado_actual': estado_actual,
                'estado_color': estado_color,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'vencimiento_sla': fecha_vencimiento_str,
                'sla_restante': sla_restante,
                'sla_color': sla_color,
                'alertas': alertas,
                'acciones': acciones,
                'id': solicitud.id,
                'etapa_color': etapa_color,
            })

        # Para vista kanban, agrupar por etapas
        if view_type == 'kanban':
            etapas_kanban = pipeline.etapas.all().order_by('orden')
            solicitudes_por_etapa = {}
            for etapa in etapas_kanban:
                solicitudes_por_etapa[etapa] = solicitudes.filter(etapa_actual=etapa)
            solicitudes_completadas = solicitudes.filter(etapa_actual__isnull=True)
            if solicitudes_completadas.exists():
                solicitudes_por_etapa['completadas'] = solicitudes_completadas
        else:
            solicitudes_por_etapa = None
            etapas_kanban = None
        
        context = {
            'pipeline': pipeline,
            'pipelines': pipelines,
            'solicitudes': solicitudes,
            'page_obj': page_obj,
            'solicitudes_tabla': solicitudes_tabla,
            'view_type': view_type,
            'solicitudes_por_etapa': solicitudes_por_etapa,
            'etapas_kanban': etapas_kanban,
            'filtros': {
                'estado': filtro_estado,
                'asignado': filtro_asignado,
                'fecha': filtro_fecha,
                'busqueda': busqueda,
                'sla': filtro_sla,
                'ordenar': ordenar_por,
            }
        }
    else:
        # Si no hay pipeline seleccionado, mostrar lista de pipelines
        context = {
            'pipelines': pipelines,
            'view_type': view_type,
        }
    
    return render(request, 'workflow/negocios.html', context)


@login_required
def bandeja_trabajo(request):
    """Bandeja de trabajo del usuario"""
    
    # Obtener solicitudes asignadas al usuario
    solicitudes_asignadas = Solicitud.objects.filter(
        asignada_a=request.user
    ).select_related('tipo_solicitud', 'pipeline', 'etapa_actual', 'subestado_actual')
    
    # Obtener bandejas grupales
    grupos_usuario = request.user.groups.all()
    etapas_grupales = Etapa.objects.filter(
        es_bandeja_grupal=True,
        permisos__grupo__in=grupos_usuario,
        permisos__puede_autoasignar=True
    )
    
    solicitudes_grupales = Solicitud.objects.filter(
        etapa_actual__in=etapas_grupales,
        asignada_a__isnull=True
    ).select_related('tipo_solicitud', 'pipeline', 'etapa_actual', 'subestado_actual')
    
    # Filtros
    filtro_estado = request.GET.get('estado', '')
    filtro_pipeline = request.GET.get('pipeline', '')
    
    if filtro_estado == 'vencidas':
        solicitudes_asignadas = solicitudes_asignadas.filter(
            fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
        )
        solicitudes_grupales = solicitudes_grupales.filter(
            fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
        )
    
    if filtro_pipeline:
        solicitudes_asignadas = solicitudes_asignadas.filter(pipeline_id=filtro_pipeline)
        solicitudes_grupales = solicitudes_grupales.filter(pipeline_id=filtro_pipeline)
    
    # Paginación
    todas_solicitudes = list(solicitudes_asignadas) + list(solicitudes_grupales)
    paginator = Paginator(todas_solicitudes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'solicitudes_asignadas': solicitudes_asignadas,
        'solicitudes_grupales': solicitudes_grupales,
        'pipelines': Pipeline.objects.all(),
        'filtros': {
            'estado': filtro_estado,
            'pipeline': filtro_pipeline,
        }
    }
    
    return render(request, 'workflow/bandeja_trabajo.html', context)


@login_required
def nueva_solicitud(request):
    """Crear una nueva solicitud"""
    
    if request.method == 'POST':
        pipeline_id = request.POST.get('pipeline')
        
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Generar código único
            import uuid
            codigo = f"{pipeline.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
            
            # Obtener primera etapa del pipeline
            primera_etapa = pipeline.etapas.order_by('orden').first()
            
            # Crear solicitud
            solicitud = Solicitud.objects.create(
                codigo=codigo,
                pipeline=pipeline,
                etapa_actual=primera_etapa,
                creada_por=request.user
            )
            
            # Crear historial inicial
            if primera_etapa:
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa=primera_etapa,
                    usuario_responsable=request.user,
                    fecha_inicio=timezone.now()
                )
            
            # Crear requisitos automáticamente
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline
            )
            
            for req_pipeline in requisitos_pipeline:
                RequisitoSolicitud.objects.create(
                    solicitud=solicitud,
                    requisito=req_pipeline.requisito
                )
            
            messages.success(request, f'Solicitud {codigo} creada exitosamente.')
            return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    context = {
        'pipelines': Pipeline.objects.all(),
    }
    
    return render(request, 'workflow/nueva_solicitud.html', context)


@login_required
def detalle_solicitud(request, solicitud_id):
    """Detalle de una solicitud específica"""
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar permisos
    if solicitud.asignada_a and solicitud.asignada_a != request.user:
        grupos_usuario = request.user.groups.all()
        tiene_permiso = PermisoEtapa.objects.filter(
            etapa=solicitud.etapa_actual,
            grupo__in=grupos_usuario,
            puede_ver=True
        ).exists()
        
        if not tiene_permiso:
            messages.error(request, 'No tienes permisos para ver esta solicitud.')
            return redirect('bandeja_trabajo')
    
    # Obtener transiciones disponibles
    transiciones_disponibles = []
    if solicitud.etapa_actual:
        transiciones = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual
        )
        
        for transicion in transiciones:
            if not transicion.requiere_permiso:
                transiciones_disponibles.append(transicion)
            else:
                # Verificar si el usuario tiene permisos específicos
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=transicion.etapa_destino,
                    grupo__in=grupos_usuario
                ).exists()
                if tiene_permiso:
                    transiciones_disponibles.append(transicion)
    
    # Obtener historial
    historial = solicitud.historial.all().order_by('-fecha_inicio')
    
    # Obtener requisitos
    requisitos = solicitud.requisitos.all()
    
    # Obtener campos personalizados
    campos_personalizados = CampoPersonalizado.objects.filter(pipeline=solicitud.pipeline)
    valores_campos = solicitud.valores_personalizados.all()
    
    context = {
        'solicitud': solicitud,
        'transiciones_disponibles': transiciones_disponibles,
        'historial': historial,
        'requisitos': requisitos,
        'campos_personalizados': campos_personalizados,
        'valores_campos': valores_campos,
    }
    
    return render(request, 'workflow/detalle_solicitud.html', context)


@login_required
def transicion_solicitud(request, solicitud_id):
    """Realizar transición de una solicitud"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        transicion_id = request.POST.get('transicion_id')
        
        if transicion_id:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Verificar que la transición es válida
            if transicion.pipeline != solicitud.pipeline or transicion.etapa_origen != solicitud.etapa_actual:
                messages.error(request, 'Transición no válida.')
                return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Verificar permisos si es necesario
            if transicion.requiere_permiso:
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=transicion.etapa_destino,
                    grupo__in=grupos_usuario
                ).exists()
                if not tiene_permiso:
                    messages.error(request, 'No tienes permisos para realizar esta transición.')
                    return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Verificar requisitos obligatorios
            requisitos_pendientes = solicitud.requisitos.filter(
                requisito__requisitopipelinetipo__obligatorio=True,
                cumplido=False
            )
            
            if requisitos_pendientes.exists():
                messages.error(request, 'Debes cumplir todos los requisitos obligatorios antes de continuar.')
                return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Cerrar historial actual
            historial_actual = solicitud.historial.filter(fecha_fin__isnull=True).first()
            if historial_actual:
                historial_actual.fecha_fin = timezone.now()
                historial_actual.save()
            
            # Actualizar solicitud
            solicitud.etapa_actual = transicion.etapa_destino
            solicitud.subestado_actual = None  # Resetear subestado
            solicitud.save()
            
            # Crear nuevo historial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=transicion.etapa_destino,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now()
            )
            
            messages.success(request, f'Solicitud movida a {transicion.etapa_destino.nombre}')
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    return redirect('detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def auto_asignar_solicitud(request, solicitud_id):
    """Auto-asignar una solicitud de bandeja grupal"""
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud está en bandeja grupal
    if not solicitud.etapa_actual.es_bandeja_grupal or solicitud.asignada_a:
        messages.error(request, 'Esta solicitud no está disponible para auto-asignación.')
        return redirect('bandeja_trabajo')
    
    # Verificar permisos
    grupos_usuario = request.user.groups.all()
    tiene_permiso = PermisoEtapa.objects.filter(
        etapa=solicitud.etapa_actual,
        grupo__in=grupos_usuario,
        puede_autoasignar=True
    ).exists()
    
    if not tiene_permiso:
        messages.error(request, 'No tienes permisos para auto-asignar solicitudes en esta etapa.')
        return redirect('bandeja_trabajo')
    
    # Asignar solicitud
    solicitud.asignada_a = request.user
    solicitud.save()
    
    messages.success(request, f'Solicitud {solicitud.codigo} asignada exitosamente.')
    return redirect('detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def actualizar_requisito(request, solicitud_id, requisito_id):
    """Actualizar estado de un requisito"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_id, solicitud=solicitud)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_ver=True
            ).exists()
            
            if not tiene_permiso:
                return JsonResponse({'error': 'No tienes permisos para actualizar esta solicitud.'}, status=403)
        
        # Actualizar requisito
        cumplido = request.POST.get('cumplido') == 'true'
        observaciones = request.POST.get('observaciones', '')
        
        requisito_solicitud.cumplido = cumplido
        requisito_solicitud.observaciones = observaciones
        
        # Manejar archivo si se sube
        if 'archivo' in request.FILES:
            requisito_solicitud.archivo = request.FILES['archivo']
        
        requisito_solicitud.save()
        
        return JsonResponse({
            'success': True,
            'cumplido': cumplido,
            'observaciones': observaciones
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def actualizar_campo_personalizado(request, solicitud_id):
    """Actualizar campos personalizados de una solicitud"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_ver=True
            ).exists()
            
            if not tiene_permiso:
                return JsonResponse({'error': 'No tienes permisos para actualizar esta solicitud.'}, status=403)
        
        campos_personalizados = CampoPersonalizado.objects.filter(pipeline=solicitud.pipeline)
        
        for campo in campos_personalizados:
            valor_campo, created = ValorCampoSolicitud.objects.get_or_create(
                solicitud=solicitud,
                campo=campo
            )
            
            valor = request.POST.get(f'campo_{campo.id}')
            
            if campo.tipo == 'texto':
                valor_campo.valor_texto = valor
            elif campo.tipo == 'numero':
                valor_campo.valor_numero = float(valor) if valor else None
            elif campo.tipo == 'entero':
                valor_campo.valor_entero = int(valor) if valor else None
            elif campo.tipo == 'fecha':
                valor_campo.valor_fecha = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
            elif campo.tipo == 'booleano':
                valor_campo.valor_booleano = valor == 'true'
            
            valor_campo.save()
        
        messages.success(request, 'Campos personalizados actualizados exitosamente.')
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ==========================================
# VISTAS DE ADMINISTRACIÓN
# ==========================================

@login_required
@permission_required('workflow.add_pipeline')
def administrar_pipelines(request):
    """Administración de pipelines"""
    
    pipelines = Pipeline.objects.all().prefetch_related('etapas')
    
    context = {
        'pipelines': pipelines,
    }
    
    return render(request, 'workflow/admin/pipelines.html', context)


@login_required
@permission_required('workflow.add_requisito')
def administrar_requisitos(request):
    """Administración de requisitos"""
    
    requisitos = Requisito.objects.all()
    requisitos_pipeline = RequisitoPipeline.objects.all().select_related('pipeline', 'requisito')
    
    context = {
        'requisitos': requisitos,
        'requisitos_pipeline': requisitos_pipeline,
    }
    
    return render(request, 'workflow/admin/requisitos.html', context)


@login_required
@permission_required('workflow.add_campopersonalizado')
def administrar_campos_personalizados(request):
    """Administración de campos personalizados"""
    
    campos = CampoPersonalizado.objects.all().select_related('pipeline')
    
    context = {
        'campos': campos,
    }
    
    return render(request, 'workflow/admin/campos_personalizados.html', context)


# ==========================================
# VISTAS DE REPORTES
# ==========================================

@login_required
def reportes_workflow(request):
    """Reportes del sistema de workflow"""
    
    # Estadísticas generales
    total_solicitudes = Solicitud.objects.count()
    solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = Solicitud.objects.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    solicitudes_por_pipeline = Pipeline.objects.annotate(
        total=Count('solicitud')
    ).values('nombre', 'total')
    
    # Solicitudes vencidas
    solicitudes_vencidas = Solicitud.objects.filter(
        etapa_actual__isnull=False
    ).extra(
        where=['fecha_ultima_actualizacion < NOW() - INTERVAL etapa_actual_sla']
    ).count()
    
    # Tiempo promedio por etapa
    tiempos_promedio = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).extra(
        select={'tiempo': 'EXTRACT(EPOCH FROM (fecha_fin - fecha_inicio))/3600'}
    ).values('etapa__nombre').annotate(
        tiempo_promedio=Avg('tiempo')
    )
    
    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': solicitudes_por_pipeline,
        'tiempos_promedio': tiempos_promedio,
    }
    
    return render(request, 'workflow/reportes.html', context)


# ==========================================
# VISTAS DE API PARA PIPELINES
# ==========================================

@login_required
@permission_required('workflow.add_pipeline')
def api_crear_pipeline(request):
    """API para crear un nuevo pipeline"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            pipeline = Pipeline.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'pipeline': {
                    'id': pipeline.id,
                    'nombre': pipeline.nombre,
                    'descripcion': pipeline.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.change_pipeline')
def api_editar_pipeline(request, pipeline_id):
    """API para editar un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            pipeline.nombre = nombre
            pipeline.descripcion = descripcion
            pipeline.save()
            
            return JsonResponse({
                'success': True,
                'pipeline': {
                    'id': pipeline.id,
                    'nombre': pipeline.nombre,
                    'descripcion': pipeline.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.delete_pipeline')
def api_eliminar_pipeline(request, pipeline_id):
    """API para eliminar un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Verificar que no hay solicitudes activas
            if pipeline.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un pipeline con solicitudes activas'
                })
            
            pipeline.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.add_etapa')
def api_obtener_etapas(request, pipeline_id):
    """API para obtener etapas de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        etapas = pipeline.etapas.all().order_by('orden')
        
        datos_etapas = []
        for etapa in etapas:
            datos_etapas.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla': str(etapa.sla),
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'subestados': list(etapa.subestados.values('id', 'nombre', 'orden')),
                'permisos': list(etapa.permisos.values('grupo__name', 'puede_ver', 'puede_autoasignar'))
            })
        
        return JsonResponse({
            'success': True,
            'pipeline_nombre': pipeline.nombre,
            'etapas': datos_etapas
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('workflow.add_etapa')
def api_crear_etapa(request, pipeline_id):
    """API para crear una nueva etapa"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden')
            sla_horas = request.POST.get('sla_horas', 24)
            es_bandeja_grupal = request.POST.get('es_bandeja_grupal') == 'true'
            
            if not nombre or not orden:
                return JsonResponse({'success': False, 'error': 'Nombre y orden son obligatorios'})
            
            # Convertir SLA a timedelta
            sla = timedelta(hours=int(sla_horas))
            
            etapa = Etapa.objects.create(
                pipeline=pipeline,
                nombre=nombre,
                orden=int(orden),
                sla=sla,
                es_bandeja_grupal=es_bandeja_grupal
            )
            
            return JsonResponse({
                'success': True,
                'etapa': {
                    'id': etapa.id,
                    'nombre': etapa.nombre,
                    'orden': etapa.orden,
                    'sla': str(etapa.sla),
                    'es_bandeja_grupal': etapa.es_bandeja_grupal
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.change_etapa')
def api_editar_etapa(request, etapa_id):
    """API para editar una etapa"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden')
            sla_horas = request.POST.get('sla_horas', 24)
            es_bandeja_grupal = request.POST.get('es_bandeja_grupal') == 'true'
            
            if not nombre or not orden:
                return JsonResponse({'success': False, 'error': 'Nombre y orden son obligatorios'})
            
            # Convertir SLA a timedelta
            sla = timedelta(hours=int(sla_horas))
            
            etapa.nombre = nombre
            etapa.orden = int(orden)
            etapa.sla = sla
            etapa.es_bandeja_grupal = es_bandeja_grupal
            etapa.save()
            
            return JsonResponse({
                'success': True,
                'etapa': {
                    'id': etapa.id,
                    'nombre': etapa.nombre,
                    'orden': etapa.orden,
                    'sla': str(etapa.sla),
                    'es_bandeja_grupal': etapa.es_bandeja_grupal
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.delete_etapa')
def api_eliminar_etapa(request, etapa_id):
    """API para eliminar una etapa"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            # Verificar que no hay solicitudes en esta etapa
            if etapa.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar una etapa con solicitudes activas'
                })
            
            etapa.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.add_subestado')
def api_crear_subestado(request, etapa_id):
    """API para crear un subestado"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden', 0)
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            subestado = SubEstado.objects.create(
                etapa=etapa,
                pipeline=etapa.pipeline,
                nombre=nombre,
                orden=int(orden)
            )
            
            return JsonResponse({
                'success': True,
                'subestado': {
                    'id': subestado.id,
                    'nombre': subestado.nombre,
                    'orden': subestado.orden
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.add_transicionetapa')
def api_crear_transicion(request, pipeline_id):
    """API para crear una transición"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            etapa_origen_id = request.POST.get('etapa_origen')
            etapa_destino_id = request.POST.get('etapa_destino')
            nombre = request.POST.get('nombre')
            requiere_permiso = request.POST.get('requiere_permiso') == 'true'
            
            if not all([etapa_origen_id, etapa_destino_id, nombre]):
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'})
            
            etapa_origen = get_object_or_404(Etapa, id=etapa_origen_id, pipeline=pipeline)
            etapa_destino = get_object_or_404(Etapa, id=etapa_destino_id, pipeline=pipeline)
            
            transicion = TransicionEtapa.objects.create(
                pipeline=pipeline,
                etapa_origen=etapa_origen,
                etapa_destino=etapa_destino,
                nombre=nombre,
                requiere_permiso=requiere_permiso
            )
            
            return JsonResponse({
                'success': True,
                'transicion': {
                    'id': transicion.id,
                    'nombre': transicion.nombre,
                    'etapa_origen': transicion.etapa_origen.nombre,
                    'etapa_destino': transicion.etapa_destino.nombre,
                    'requiere_permiso': transicion.requiere_permiso
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.add_requisito')
def api_crear_requisito(request):
    """API para crear un requisito"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            requisito = Requisito.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'requisito': {
                    'id': requisito.id,
                    'nombre': requisito.nombre,
                    'descripcion': requisito.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.add_requisitopipeline')
def api_asignar_requisito_pipeline(request, pipeline_id):
    """API para asignar un requisito a un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            requisito_id = request.POST.get('requisito_id')
            obligatorio = request.POST.get('obligatorio') == 'true'
            
            if not requisito_id:
                return JsonResponse({'success': False, 'error': 'El requisito es obligatorio'})
            
            requisito = get_object_or_404(Requisito, id=requisito_id)
            
            requisito_pipeline, created = RequisitoPipeline.objects.get_or_create(
                pipeline=pipeline,
                requisito=requisito,
                defaults={'obligatorio': obligatorio}
            )
            
            if not created:
                requisito_pipeline.obligatorio = obligatorio
                requisito_pipeline.save()
            
            return JsonResponse({
                'success': True,
                'requisito_pipeline': {
                    'id': requisito_pipeline.id,
                    'requisito_nombre': requisito.nombre,
                    'obligatorio': requisito_pipeline.obligatorio
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.add_campopersonalizado')
def api_crear_campo_personalizado(request, pipeline_id):
    """API para crear un campo personalizado"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            requerido = request.POST.get('requerido') == 'true'
            
            if not all([nombre, tipo]):
                return JsonResponse({'success': False, 'error': 'Nombre y tipo son obligatorios'})
            
            campo = CampoPersonalizado.objects.create(
                pipeline=pipeline,
                nombre=nombre,
                tipo=tipo,
                requerido=requerido
            )
            
            return JsonResponse({
                'success': True,
                'campo': {
                    'id': campo.id,
                    'nombre': campo.nombre,
                    'tipo': campo.tipo,
                    'requerido': campo.requerido
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_obtener_datos_pipeline(request, pipeline_id):
    """API para obtener todos los datos de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Etapas
        etapas = pipeline.etapas.all().order_by('orden')
        datos_etapas = []
        for etapa in etapas:
            datos_etapas.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla': str(etapa.sla),
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'subestados': list(etapa.subestados.values('id', 'nombre', 'orden')),
                'permisos': list(etapa.permisos.values('grupo__name', 'puede_ver', 'puede_autoasignar'))
            })
        
        # Transiciones
        transiciones = pipeline.transiciones.all()
        datos_transiciones = []
        for transicion in transiciones:
            datos_transiciones.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': transicion.etapa_origen.nombre,
                'etapa_destino': transicion.etapa_destino.nombre,
                'requiere_permiso': transicion.requiere_permiso
            })
        
        # Requisitos
        requisitos_pipeline = pipeline.requisitos_pipeline.all().select_related('requisito')
        datos_requisitos = []
        for req_pipeline in requisitos_pipeline:
            datos_requisitos.append({
                'id': req_pipeline.id,
                'requisito_nombre': req_pipeline.requisito.nombre,
                'obligatorio': req_pipeline.obligatorio
            })
        
        # Campos personalizados
        campos = pipeline.campos_personalizados.all()
        datos_campos = []
        for campo in campos:
            datos_campos.append({
                'id': campo.id,
                'nombre': campo.nombre,
                'tipo': campo.tipo,
                'requerido': campo.requerido
            })
        
        return JsonResponse({
            'success': True,
            'pipeline': {
                'id': pipeline.id,
                'nombre': pipeline.nombre,
                'descripcion': pipeline.descripcion
            },
            'etapas': datos_etapas,
            'transiciones': datos_transiciones,
            'requisitos': datos_requisitos,
            'campos_personalizados': datos_campos
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# VISTAS DE API
# ==========================================

def api_solicitudes(request):
    """API para obtener solicitudes"""
    
    solicitudes = Solicitud.objects.all().select_related(
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


def api_estadisticas(request):
    """API para obtener estadísticas"""
    
    # Estadísticas básicas
    total_solicitudes = Solicitud.objects.count()
    solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = Solicitud.objects.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    solicitudes_por_pipeline = Pipeline.objects.annotate(
        total=Count('solicitud')
    ).values('nombre', 'total')
    
    # Solicitudes vencidas
    solicitudes_vencidas = Solicitud.objects.filter(
        etapa_actual__isnull=False
    ).extra(
        where=['fecha_ultima_actualizacion < NOW() - INTERVAL etapa_actual_sla']
    ).count()
    
    return JsonResponse({
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': list(solicitudes_por_pipeline),
    })


def sitio_construccion(request):
    """Vista para página de sitio en construcción"""
    return render(request, 'workflow/sitio_construccion.html') 