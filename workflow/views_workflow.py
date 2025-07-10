from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .modelsWorkflow import *
from .models import ClienteEntrevista
from pacifico.models import UserProfile, Cliente, Cotizacion
import json
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import time
import threading
import queue
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

# ==========================================
# VISTAS PRINCIPALES DEL WORKFLOW
# ==========================================

@login_required
def dashboard_workflow(request):
    """Dashboard principal del sistema de workflow"""
    
    # Obtener solicitudes del usuario
    solicitudes_asignadas = Solicitud.objects.filter(
        asignada_a=request.user
    ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    
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
    ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    
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
        # Guardar último pipeline visitado en la sesión
        request.session['ultimo_pipeline_id'] = pipeline_id
        
        # Obtener el rol del usuario desde UserProfile
        user_role = 'Usuario'  # Rol por defecto
        
        # Verificar primero si es superuser
        if request.user.is_superuser:
            user_role = 'Administrador'
        else:
            # Si no es superuser, verificar UserProfile
            try:
                user_profile = request.user.userprofile
                user_role = user_profile.rol
            except Exception:
                # Si no tiene UserProfile, mantener rol por defecto
                pass
        
        # === SISTEMA DE PERMISOS SUPER STAFF ===
        # Los usuarios super staff (is_staff=True) pueden ver TODO
        if request.user.is_staff:
            # Super staff ve TODAS las solicitudes del pipeline
            solicitudes = Solicitud.objects.filter(pipeline=pipeline).select_related(
                'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a'
            )
        else:
            # Lógica de permisos basada en rol para usuarios regulares
            if user_role == 'Administrador':
                # Administrador ve TODAS las solicitudes
                solicitudes = Solicitud.objects.filter(pipeline=pipeline).select_related(
                    'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                    'creada_por', 'asignada_a'
                )
            elif user_role == 'Supervisor':
                # Supervisor ve todas las solicitudes de su(s) grupo(s)
                user_groups = request.user.groups.all()
                if user_groups.exists():
                    group_users = User.objects.filter(groups__in=user_groups)
                    solicitudes = Solicitud.objects.filter(pipeline=pipeline, creada_por__in=group_users).select_related(
                        'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                        'creada_por', 'asignada_a'
                    )
                else:
                    # Si no tiene grupos asignados, solo ve las suyas
                    solicitudes = Solicitud.objects.filter(pipeline=pipeline, creada_por=request.user).select_related(
                        'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                        'creada_por', 'asignada_a'
                    )
            else:
                # Oficial y Usuario solo ven sus propias solicitudes
                solicitudes = Solicitud.objects.filter(pipeline=pipeline, creada_por=request.user).select_related(
                    'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
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
            # === DEBUG TEMPORAL ===
            if solicitud.codigo == 'PRU-4811C164':
                print(f"DEBUG - Solicitud {solicitud.codigo}:")
                print(f"  - Cliente: {solicitud.cliente}")
                print(f"  - Cotización: {solicitud.cotizacion}")
                if solicitud.cotizacion:
                    print(f"  - Cotización nombreCliente: {solicitud.cotizacion.nombreCliente}")
                    print(f"  - Cotización cedulaCliente: {solicitud.cotizacion.cedulaCliente}")
                    print(f"  - Cotización montoPrestamo: {solicitud.cotizacion.montoPrestamo}")
                    print(f"  - Cotización tipoPrestamo: {solicitud.cotizacion.tipoPrestamo}")
                if solicitud.cliente:
                    print(f"  - Cliente nombreCliente: {solicitud.cliente.nombreCliente}")
                    print(f"  - Cliente cedulaCliente: {solicitud.cliente.cedulaCliente}")
                print(f"  - Propiedades:")
                print(f"    - cliente_nombre: {solicitud.cliente_nombre}")
                print(f"    - cliente_cedula: {solicitud.cliente_cedula}")
                print(f"    - producto_descripcion: {solicitud.producto_descripcion}")
                print(f"    - monto_formateado: {solicitud.monto_formateado}")
            # === FIN DEBUG ===

            # Campos personalizados
            valores = {v.campo.nombre.lower(): v for v in solicitud.valores_personalizados.select_related('campo').all()}
            get_valor = lambda nombre: valores.get(nombre.lower()).valor() if valores.get(nombre.lower()) else None

            # Cliente, cédula, producto y monto usando las nuevas propiedades del modelo
            cliente = solicitud.cliente_nombre
            cedula = solicitud.cliente_cedula
            producto = solicitud.producto_descripcion
            monto_formateado = solicitud.monto_formateado

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
                'cliente_nombre': cliente,
                'cliente_cedula': cedula,
                'producto_descripcion': producto,
                'monto_formateado': monto_formateado,
                # Mantener compatibilidad con código existente
                'cliente': cliente,
                'cedula': cedula,
                'producto': producto,
                'monto': monto_formateado,
                'propietario': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
                'asignado_a': (solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username) if solicitud.asignada_a else 'Sin asignar',
                'etapa': solicitud.etapa_actual.nombre if solicitud.etapa_actual else '',
                'estado_actual': estado_actual,
                'estado_color': estado_color,
                'fecha_inicio': fecha_inicio,
                'fecha_inicio_str': fecha_inicio.strftime('%d/%m/%Y'),
                'vencimiento_sla': vencimiento_sla,
                'vencimiento_sla_str': fecha_vencimiento_str,
                'sla_restante': sla_restante,
                'sla_color': sla_color,
                'alertas': alertas,
                'acciones': acciones,
                'id': solicitud.id,
                'etapa_color': etapa_color,
                'prioridad': solicitud.prioridad or '',
                'etiquetas_oficial': solicitud.etiquetas_oficial or '',
            })

        # Para vista kanban, crear datos enriquecidos por etapa
        if view_type == 'kanban':
            etapas_kanban = pipeline.etapas.all().order_by('orden')
            solicitudes_por_etapa = {}
            
            # Crear diccionario con todas las solicitudes enriquecidas
            solicitudes_dict = {s['id']: s for s in solicitudes_tabla}
            
            for etapa in etapas_kanban:
                solicitudes_etapa = solicitudes.filter(etapa_actual=etapa)
                solicitudes_por_etapa[etapa.id] = [
                    solicitudes_dict.get(sol.id, {
                        'id': sol.id,
                        'codigo': sol.codigo,
                        'cliente_nombre': sol.cliente_nombre,
                        'cliente_cedula': sol.cliente_cedula,
                        'producto_descripcion': sol.producto_descripcion,
                        'monto_formateado': sol.monto_formateado,
                        # Mantener compatibilidad
                        'cliente': sol.cliente_nombre,
                        'monto': sol.monto_formateado,
                        'asignado_a': 'Sin asignar',
                        'sla_restante': 'N/A',
                        'sla_color': 'text-secondary',
                        'estado_actual': 'En proceso',
                        'estado_color': 'primary',
                        'fecha_inicio': sol.fecha_creacion.strftime('%d/%m/%Y'),
                        'prioridad': sol.prioridad or '',
                        'etapa_actual': sol.etapa_actual
                    }) for sol in solicitudes_etapa
                ]
        else:
            solicitudes_por_etapa = None
            etapas_kanban = None
        
        etiquetas_predefinidas = [
            "📞 No responde", "🗓️ Cita agendada", "✅ Documentos completos", "📎 Falta carta trabajo",
            "🔄 Seguimiento en 48h", "💬 WhatsApp activo", "⚠️ Cliente indeciso", "🚀 Cliente caliente",
            "🕐 Esperando confirmación", "🧾 Enviado a crédito", "🔒 En validación", "❌ Caso descartado"
        ]
        
        # Obtener lista de oficiales para el drawer
        oficiales = User.objects.filter(
            userprofile__rol__in=['Oficial', 'Supervisor', 'Administrador']
        ).values_list('username', flat=True).distinct()
        
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
            },
            'prioridades_posibles': ['Alta', 'Media', 'Baja'],
            'etiquetas_predefinidas': etiquetas_predefinidas,
            'user_role': user_role,  # Agregar rol del usuario al contexto
            'oficiales': oficiales,  # Para el drawer
        }
    else:
        # Si no hay pipeline seleccionado, mostrar lista de pipelines
        # Obtener lista de oficiales para el drawer
        oficiales = User.objects.filter(
            userprofile__rol__in=['Oficial', 'Supervisor', 'Administrador']
        ).values_list('username', flat=True).distinct()
        
        context = {
            'pipelines': pipelines,
            'view_type': view_type,
            'oficiales': oficiales,  # Para el drawer
        }
    
    return render(request, 'workflow/negocios.html', context)


@login_required
def bandeja_trabajo(request):
    """Bandeja de trabajo del usuario"""
    
    # === SISTEMA DE PERMISOS SUPER STAFF ===
    # Los usuarios super staff (is_staff=True) pueden ver TODO
    if request.user.is_staff:
        # Super staff ve TODAS las solicitudes asignadas
        solicitudes_asignadas = Solicitud.objects.filter(
            asignada_a__isnull=False
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
        # Super staff ve TODAS las bandejas grupales
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True)
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
    else:
        # Usuarios regulares - permisos normales
        # Obtener solicitudes asignadas al usuario
        solicitudes_asignadas = Solicitud.objects.filter(
            asignada_a=request.user
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
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
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
    
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
        cliente_id = request.POST.get('cliente')
        cotizacion_id = request.POST.get('cotizacion')
        
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Generar código único
            import uuid
            codigo = f"{pipeline.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
            
            # Obtener primera etapa del pipeline
            primera_etapa = pipeline.etapas.order_by('orden').first()
            
            # Obtener cliente y cotización si se proporcionaron
            cliente = None
            cotizacion = None
            
            if cliente_id:
                cliente = get_object_or_404(Cliente, id=cliente_id)
            
            if cotizacion_id:
                cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
            
            # Crear solicitud
            solicitud = Solicitud.objects.create(
                codigo=codigo,
                pipeline=pipeline,
                etapa_actual=primera_etapa,
                creada_por=request.user,
                cliente=cliente,
                cotizacion=cotizacion
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
                requisito_solicitud = RequisitoSolicitud.objects.create(
                    solicitud=solicitud,
                    requisito=req_pipeline.requisito
                )
                
                # Verificar si hay archivo subido para este requisito
                archivo_key = f'archivo_requisito_{req_pipeline.requisito.id}'
                if archivo_key in request.FILES:
                    requisito_solicitud.archivo = request.FILES[archivo_key]
                    requisito_solicitud.save()
            
            # Guardar campos personalizados
            campos_personalizados = CampoPersonalizado.objects.filter(pipeline=pipeline)
            for campo in campos_personalizados:
                valor = request.POST.get(f'campo_{campo.id}')
                if valor:
                    valor_campo = ValorCampoSolicitud.objects.create(
                        solicitud=solicitud,
                        campo=campo
                    )
                    
                    # Guardar según el tipo de campo
                    if campo.tipo == 'texto':
                        valor_campo.valor_texto = valor
                    elif campo.tipo == 'numero':
                        valor_campo.valor_numero = float(valor) if valor else None
                    elif campo.tipo == 'entero':
                        valor_campo.valor_entero = int(valor) if valor else None
                    elif campo.tipo == 'fecha':
                        from datetime import datetime
                        valor_campo.valor_fecha = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
                    elif campo.tipo == 'booleano':
                        valor_campo.valor_booleano = valor == 'true'
                    
                    valor_campo.save()
            
            # Responder con JSON para requests AJAX
            if request.content_type == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'solicitud_id': solicitud.id,
                    'codigo': solicitud.codigo,
                    'message': f'Solicitud {codigo} creada exitosamente.'
                })
            
            messages.success(request, f'Solicitud {codigo} creada exitosamente.')
            return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Obtener clientes y cotizaciones para el formulario
    
    # Obtener clientes del usuario actual o todos si es superuser
    if request.user.is_superuser:
        clientes = Cliente.objects.all().order_by('-created_at')[:100]  # Últimos 100 clientes
    else:
        clientes = Cliente.objects.filter(
            Q(added_by=request.user) | 
            Q(propietario=request.user)
        ).order_by('-created_at')[:100]
    
    # Obtener cotizaciones del usuario actual o todas si es superuser
    if request.user.is_superuser:
        cotizaciones = Cotizacion.objects.all().order_by('-created_at')[:100]  # Últimas 100 cotizaciones
    else:
        cotizaciones = Cotizacion.objects.filter(added_by=request.user).order_by('-created_at')[:100]
    
    context = {
        'pipelines': Pipeline.objects.all(),
        'clientes': clientes,
        'cotizaciones': cotizaciones,
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


@login_required
def administrar_usuarios(request):
    """Vista para administrar usuarios y grupos - Solo para administradores"""
    
    # Verificar permisos de administrador
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('workflow:dashboard')
    
    # Obtener usuarios y grupos
    usuarios = User.objects.select_related('userprofile').all().order_by('username')
    grupos = Group.objects.all().order_by('name')
    
    # Estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_inactivos = total_usuarios - usuarios_activos
    total_grupos = grupos.count()
    
    # Usuarios por grupo
    usuarios_por_grupo = {}
    for grupo in grupos:
        usuarios_por_grupo[grupo.name] = grupo.user_set.count()
    
    # Usuarios sin grupos
    usuarios_sin_grupos = usuarios.filter(groups__isnull=True).count()
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'total_grupos': total_grupos,
        'usuarios_por_grupo': usuarios_por_grupo,
        'usuarios_sin_grupos': usuarios_sin_grupos,
    }
    
    return render(request, 'workflow/admin/usuarios.html', context)


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


@login_required
def api_actualizar_prioridad(request, solicitud_id):
    """API para actualizar la prioridad de una solicitud"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            prioridad = data.get('prioridad', '').strip()
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            # Eliminar validación de permisos, permitir a cualquier usuario
            prioridades_validas = ['Alta', 'Media', 'Baja']
            if prioridad and prioridad not in prioridades_validas:
                return JsonResponse({'success': False, 'error': 'Prioridad no válida'})
            solicitud.prioridad = prioridad
            solicitud.save()
            return JsonResponse({'success': True, 'prioridad': prioridad})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_actualizar_etiquetas(request, solicitud_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        etiquetas = data.get('etiquetas_oficial', '')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        # Limpiar espacios de cada etiqueta
        etiquetas_limpias = ','.join([e.strip() for e in etiquetas.split(',') if e.strip()])
        solicitud.etiquetas_oficial = etiquetas_limpias
        solicitud.save()
        return JsonResponse({'success': True, 'etiquetas_oficial': etiquetas_limpias})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_buscar_clientes(request):
    """API para buscar clientes"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return JsonResponse({'clientes': []})
        
        # Buscar clientes por nombre o cédula
        clientes = Cliente.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombre': cliente.nombreCliente or 'Sin nombre',
                'cedula': cliente.cedulaCliente or 'Sin cédula',
                'fecha_creacion': cliente.created_at.strftime('%d/%m/%Y') if cliente.created_at else '',
                'texto_completo': f"{cliente.nombreCliente or 'Sin nombre'} - {cliente.cedulaCliente or 'Sin cédula'}"
            })
        
        return JsonResponse({'clientes': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def api_buscar_cotizaciones(request):
    """API para buscar cotizaciones"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        cliente_id = request.GET.get('cliente_id', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        # Filtrar cotizaciones
        cotizaciones = Cotizacion.objects.all()
        
        # Filtrar por cliente si se especifica
        if cliente_id:
            cotizaciones = cotizaciones.filter(cedulaCliente=cliente_id)
        
        # Buscar por número de cotización, nombre de cliente o monto
        if query:
            cotizaciones = cotizaciones.filter(
                Q(NumeroCotizacion__icontains=query) |
                Q(nombreCliente__icontains=query) |
                Q(montoPrestamo__icontains=query)
            )
        
        cotizaciones = cotizaciones.order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            resultados.append({
                'id': cotizacion.id,
                'numero': cotizacion.NumeroCotizacion or cotizacion.id,
                'cliente': cotizacion.nombreCliente or 'Sin cliente',
                'monto': float(cotizacion.montoPrestamo) if cotizacion.montoPrestamo else 0,
                'tipo': cotizacion.tipoPrestamo or 'Sin tipo',
                'fecha_creacion': cotizacion.created_at.strftime('%d/%m/%Y') if cotizacion.created_at else '',
                'texto_completo': f"#{cotizacion.NumeroCotizacion or cotizacion.id} - {cotizacion.nombreCliente or 'Sin cliente'} - ${cotizacion.montoPrestamo or 0}"
            })
        
        return JsonResponse({'cotizaciones': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def api_buscar_cotizaciones_drawer(request):
    """API para buscar cotizaciones en el drawer"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'cotizaciones': []})
        
        # Buscar cotizaciones por nombre de cliente, cédula o ID
        cotizaciones = Cotizacion.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query) |
            Q(id__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            resultados.append({
                'id': cotizacion.id,
                'nombreCliente': cotizacion.nombreCliente or 'Sin nombre',
                'cedulaCliente': cotizacion.cedulaCliente or 'Sin cédula',
                'tipoPrestamo': cotizacion.tipoPrestamo or 'Sin tipo',
                'montoPrestamo': float(cotizacion.montoPrestamo) if cotizacion.montoPrestamo else 0,
                'oficial': cotizacion.oficial or 'Sin oficial',
                'created_at': cotizacion.created_at.isoformat() if cotizacion.created_at else None
            })
        
        return JsonResponse({'success': True, 'cotizaciones': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_buscar_clientes_drawer(request):
    """API para buscar clientes en el drawer"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'clientes': []})
        
        # Buscar clientes por nombre o cédula
        clientes = Cliente.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombreCliente': cliente.nombreCliente or 'Sin nombre',
                'cedulaCliente': cliente.cedulaCliente or 'Sin cédula',
                'edad': cliente.edad or 'Sin edad',
                'sexo': cliente.sexo or 'Sin sexo'
            })
        
        return JsonResponse({'success': True, 'clientes': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_formulario_datos(request):
    """API para obtener datos del formulario basado en el pipeline"""
    if request.method == 'GET':
        pipeline_id = request.GET.get('pipeline_id')
        
        if not pipeline_id:
            return JsonResponse({'success': False, 'error': 'ID de pipeline requerido'})
        
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Obtener campos personalizados del pipeline
            campos_personalizados = CampoPersonalizado.objects.filter(
                pipeline=pipeline
            ).values('id', 'nombre', 'tipo', 'requerido', 'descripcion')
            
            # Obtener requisitos del pipeline
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline
            ).select_related('requisito')
            
            requisitos = []
            for req_pipeline in requisitos_pipeline:
                requisitos.append({
                    'id': req_pipeline.requisito.id,
                    'nombre': req_pipeline.requisito.nombre,
                    'descripcion': req_pipeline.requisito.descripcion,
                    'obligatorio': req_pipeline.obligatorio
                })
            
            return JsonResponse({
                'success': True,
                'campos_personalizados': list(campos_personalizados),
                'requisitos': requisitos
            })
            
        except Pipeline.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pipeline no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ==========================================
# VISTAS PWA
# ==========================================

def offline_view(request):
    """Vista para mostrar página offline de PWA"""
    return render(request, 'workflow/offline.html')


def health_check(request):
    """Health check endpoint para PWA"""
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.1'
    })


def pwa_test_view(request):
    """PWA testing page"""
    return render(request, 'workflow/pwa_test.html')


# Sistema de notificaciones en tiempo real
class NotificationManager:
    def __init__(self):
        self.clients = {}
        self.last_update = {}
    
    def add_client(self, user_id, response_queue):
        """Agregar cliente para notificaciones"""
        self.clients[user_id] = response_queue
        self.last_update[user_id] = timezone.now()
    
    def remove_client(self, user_id):
        """Remover cliente"""
        if user_id in self.clients:
            del self.clients[user_id]
        if user_id in self.last_update:
            del self.last_update[user_id]
    
    def notify_change(self, change_type, data, affected_users=None):
        """Notificar cambio a usuarios específicos o todos"""
        if affected_users is None:
            affected_users = list(self.clients.keys())
        
        notification = {
            'type': change_type,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        
        for user_id in affected_users:
            if user_id in self.clients:
                try:
                    self.clients[user_id].put(notification)
                except:
                    # Cliente desconectado, remover
                    self.remove_client(user_id)

# Instancia global del manager
notification_manager = NotificationManager()

@login_required
def api_notifications_stream(request):
    """API de Server-Sent Events para notificaciones en tiempo real"""
    def event_stream():
        user_id = request.user.id
        response_queue = queue.Queue()
        
        # Agregar cliente
        notification_manager.add_client(user_id, response_queue)
        
        try:
            # Enviar evento inicial
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Conectado a notificaciones'})}\n\n"
            
            while True:
                try:
                    # Esperar por notificaciones con timeout
                    notification = response_queue.get(timeout=30)
                    yield f"data: {json.dumps(notification)}\n\n"
                except queue.Empty:
                    # Enviar heartbeat cada 30 segundos
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': timezone.now().isoformat()})}\n\n"
                except:
                    break
        finally:
            # Limpiar cliente al desconectar
            notification_manager.remove_client(user_id)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    return response

@login_required
def api_check_updates(request):
    """API mejorada para verificar actualizaciones con detección inteligente"""
    try:
        # Obtener timestamp de la última actualización del usuario
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        # Obtener vista actual para filtros específicos
        current_view = request.GET.get('view', 'bandejas')  # bandejas, tabla, kanban
        
        # Solicitudes del usuario según sus grupos
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Verificar cambios específicos por tipo de vista
        cambios_detectados = []
        
        # 1. Cambios en bandeja grupal (para vista bandejas)
        if current_view in ['bandejas', 'all']:
            solicitudes_grupales_nuevas = solicitudes_base.filter(
                etapa_actual__es_bandeja_grupal=True,
                asignada_a__isnull=True,
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_grupales_nuevas > 0:
                cambios_detectados.append({
                    'tipo': 'bandeja_grupal',
                    'count': solicitudes_grupales_nuevas
                })
        
        # 2. Cambios en tareas personales (para vista bandejas)
        if current_view in ['bandejas', 'all']:
            solicitudes_personales_nuevas = solicitudes_base.filter(
                asignada_a=request.user,
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_personales_nuevas > 0:
                cambios_detectados.append({
                    'tipo': 'bandeja_personal',
                    'count': solicitudes_personales_nuevas
                })
        
        # 3. Cambios generales en solicitudes (para tabla/kanban)
        if current_view in ['tabla', 'kanban', 'all']:
            solicitudes_actualizadas = solicitudes_base.filter(
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_actualizadas > 0:
                cambios_detectados.append({
                    'tipo': 'solicitudes_generales',
                    'count': solicitudes_actualizadas
                })
        
        # 4. Nuevas solicitudes creadas
        nuevas_solicitudes = solicitudes_base.filter(
            fecha_creacion__gt=last_check_time
        ).count()
        
        if nuevas_solicitudes > 0:
            cambios_detectados.append({
                'tipo': 'nuevas_solicitudes',
                'count': nuevas_solicitudes
            })
        
        # Obtener detalles de cambios para debugging
        solicitudes_modificadas = list(solicitudes_base.filter(
            fecha_ultima_actualizacion__gt=last_check_time
        ).values('id', 'codigo', 'etapa_actual__nombre', 'asignada_a__username')[:10])
        
        has_updates = len(cambios_detectados) > 0
        
        return JsonResponse({
            'success': True,
            'has_updates': has_updates,
            'cambios_detectados': cambios_detectados,
            'total_cambios': sum(c['count'] for c in cambios_detectados),
            'nuevas_solicitudes': nuevas_solicitudes,
            'solicitudes_modificadas': solicitudes_modificadas,
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': current_view
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })

# Función para notificar cambios automáticamente
def notify_solicitud_change(solicitud, change_type, user=None):
    """Notificar cambio en solicitud a usuarios relevantes"""
    try:
        # Obtener usuarios que deben ser notificados
        affected_users = []
        
        # Usuarios del grupo de la etapa actual
        if solicitud.etapa_actual:
            group_users = User.objects.filter(
                groups__in=solicitud.etapa_actual.pipeline.grupos.all()
            ).values_list('id', flat=True)
            affected_users.extend(group_users)
        
        # Usuario asignado
        if solicitud.asignada_a:
            affected_users.append(solicitud.asignada_a.id)
        
        # Datos de la notificación
        notification_data = {
            'solicitud_id': solicitud.id,
            'codigo': solicitud.codigo,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
            },
            'asignada_a': {
                'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
            },
            'user_action': {
                'id': user.id if user else None,
                'username': user.username if user else None,
                'nombre_completo': user.get_full_name() if user else None
            },
            'pipeline_id': solicitud.pipeline.id if solicitud.pipeline else None,
            'timestamp': timezone.now().isoformat()
        }
        
        # Enviar notificación
        notification_manager.notify_change(change_type, notification_data, affected_users)
        
    except Exception as e:
        print(f"Error notificando cambio: {e}")

def enviar_correo_bandeja_grupal(solicitud, etapa):
    """
    Función para enviar correo automático cuando una solicitud entra a una etapa de bandeja grupal.
    Basada en la implementación de correos de la app tómbola.
    """
    try:
        # Destinatarios fijos según especificación
        destinatarios = [
            "jacastillo@fpacifico.com",
            "arodriguez@fpacifico.com"
        ]
        
        # Construir la URL de la bandeja
        # Formato: /workflow/bandejas/?etapa_id=3
        bandeja_url = f"{getattr(settings, 'SITE_URL', 'https://pacifico.com')}/workflow/bandejas/?etapa_id={etapa.id}"
        
        # Obtener nombre del cliente
        cliente_nombre = ""
        try:
            if hasattr(solicitud, 'cliente') and solicitud.cliente:
                cliente_nombre = getattr(solicitud.cliente, 'nombreCliente', 'Sin nombre')
            elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion and solicitud.cotizacion.cliente:
                cliente_nombre = getattr(solicitud.cotizacion.cliente, 'nombreCliente', 'Sin nombre')
            else:
                cliente_nombre = "Cliente no asignado"
        except Exception as e:
            print(f"⚠️ Error obteniendo nombre del cliente: {e}")
            cliente_nombre = "Error al obtener cliente"
        
        # Contexto para el template
        context = {
            'solicitud': solicitud,
            'etapa': etapa,
            'cliente_nombre': cliente_nombre,
            'bandeja_url': bandeja_url,
        }
        
        # Cargar el template HTML
        html_content = render_to_string('workflow/emails/bandeja_grupal_notification.html', context)
        
        # Crear el asunto
        subject = f"🔔 Nueva Solicitud en Bandeja Grupal - {solicitud.codigo}"
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
        Nueva Solicitud en Bandeja Grupal
        
        Hola equipo,
        
        Una solicitud ha ingresado a una etapa de bandeja grupal y requiere atención:
        
        • Código: {solicitud.codigo}
        • Cliente: {cliente_nombre or 'Sin asignar'}
        • Pipeline: {solicitud.pipeline.nombre}
        • Etapa: {etapa.nombre}
        • Creada por: {solicitud.creada_por.get_full_name() or solicitud.creada_por.username}
        • Fecha: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        Para ver la solicitud, haz clic en el siguiente enlace:
        {bandeja_url}
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo
        email.send()
        
        print(f"✅ Correo enviado correctamente para solicitud {solicitud.codigo} - Etapa: {etapa.nombre}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo para solicitud {solicitud.codigo}: {str(e)}")


@login_required
@csrf_exempt
def api_cambiar_etapa(request, solicitud_id):
    """API para cambiar la etapa de una solicitud"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener la solicitud
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos (el usuario debe ser el creador, asignado, o tener permisos especiales)
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para cambiar esta solicitud'}, status=403)
        
        # Obtener datos del request
        data = json.loads(request.body)
        nueva_etapa_id = data.get('etapa_id')
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de etapa requerido'}, status=400)
        
        # Obtener la nueva etapa
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Verificar que la etapa sea diferente a la actual
        if solicitud.etapa_actual == nueva_etapa:
            return JsonResponse({'error': 'La solicitud ya está en esta etapa'}, status=400)
        
        # NUEVO: Verificar si existe una transición definida y validar requisitos
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if transicion:
            # Verificar requisitos obligatorios para esta transición
            requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
            if requisitos_faltantes:
                return JsonResponse({
                    'error': 'Requisitos faltantes',
                    'tipo_error': 'requisitos_faltantes',
                    'requisitos_faltantes': requisitos_faltantes,
                    'mensaje': f'Faltan {len(requisitos_faltantes)} requisito(s) obligatorio(s) para continuar a "{nueva_etapa.nombre}"'
                }, status=400)
        
        # Cerrar el historial actual si existe
        if solicitud.etapa_actual:
            historial_actual = HistorialSolicitud.objects.filter(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                fecha_fin__isnull=True
            ).first()
            
            if historial_actual:
                historial_actual.fecha_fin = timezone.now()
                historial_actual.save()
        
        # Cambiar la etapa
        etapa_anterior = solicitud.etapa_actual
        solicitud.etapa_actual = nueva_etapa
        solicitud.fecha_ultima_actualizacion = timezone.now()
        
        # Si la nueva etapa es grupal, quitar asignación individual
        if nueva_etapa.es_bandeja_grupal:
            solicitud.asignada_a = None
        
        solicitud.save()
        
        # Crear nuevo historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=nueva_etapa,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        # 🚨 CRÍTICO: Notificar cambio de etapa en tiempo real a TODAS las vistas
        notify_solicitud_change(solicitud, 'solicitud_cambio_etapa', request.user)
        
        # 📧 NUEVO: Enviar correo automático si la nueva etapa es bandeja grupal
        print(f"🔍 DEBUG: Verificando etapa {nueva_etapa.nombre} - es_bandeja_grupal: {nueva_etapa.es_bandeja_grupal}")
        if nueva_etapa.es_bandeja_grupal:
            print(f"📧 ACTIVANDO envío de correo para solicitud {solicitud.codigo} en etapa {nueva_etapa.nombre}")
            enviar_correo_bandeja_grupal(solicitud, nueva_etapa)
        else:
            print(f"ℹ️ No se envía correo - la etapa {nueva_etapa.nombre} no es bandeja grupal")
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Solicitud {solicitud.codigo} movida de "{etapa_anterior.nombre if etapa_anterior else "Sin etapa"}" a "{nueva_etapa.nombre}"',
            'nueva_etapa': {
                'id': nueva_etapa.id,
                'nombre': nueva_etapa.nombre,
                'orden': nueva_etapa.orden
            },
            'etapa_anterior': {
                'id': etapa_anterior.id if etapa_anterior else None,
                'nombre': etapa_anterior.nombre if etapa_anterior else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def verificar_requisitos_transicion(solicitud, transicion):
    """
    Verificar si faltan requisitos obligatorios para una transición específica
    """
    from .modelsWorkflow import RequisitoTransicion
    
    # Obtener requisitos obligatorios para esta transición
    requisitos_transicion = RequisitoTransicion.objects.filter(
        transicion=transicion,
        obligatorio=True
    ).select_related('requisito')
    
    requisitos_faltantes = []
    
    for req_transicion in requisitos_transicion:
        # Verificar si el requisito existe para esta solicitud
        requisito_solicitud = RequisitoSolicitud.objects.filter(
            solicitud=solicitud,
            requisito=req_transicion.requisito
        ).first()
        
        # Si no existe o no está cumplido o no tiene archivo
        if not requisito_solicitud or not requisito_solicitud.cumplido or not requisito_solicitud.archivo:
            requisitos_faltantes.append({
                'id': req_transicion.requisito.id,
                'nombre': req_transicion.requisito.nombre,
                'descripcion': req_transicion.requisito.descripcion,
                'mensaje_personalizado': req_transicion.mensaje_personalizado,
                'tiene_archivo': bool(requisito_solicitud and requisito_solicitud.archivo),
                'esta_cumplido': bool(requisito_solicitud and requisito_solicitud.cumplido),
                'requisito_solicitud_id': requisito_solicitud.id if requisito_solicitud else None
            })
    
    return requisitos_faltantes


@login_required
def vista_mixta_bandejas(request):
    """Vista mixta que combina bandeja grupal y personal"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    from .modelsWorkflow import Solicitud, Etapa, Pipeline, PermisoEtapa, HistorialSolicitud
    
    # === SISTEMA DE PERMISOS SUPER STAFF ===
    # Los usuarios super staff (is_staff=True) pueden ver TODO
    if request.user.is_staff:
        # Super staff ve TODAS las solicitudes en ambas bandejas
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True)
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).order_by('-fecha_creacion')
        
        # Super staff ve TODAS las solicitudes personales
        solicitudes_personales = Solicitud.objects.filter(
            asignada_a__isnull=False
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).order_by('-fecha_ultima_actualizacion')
    else:
        # Usuarios regulares - permisos normales
        grupos_usuario = request.user.groups.all()
        
        # === BANDEJA GRUPAL ===
        # Obtener etapas grupales donde el usuario tiene permisos
        etapas_grupales = Etapa.objects.filter(
            es_bandeja_grupal=True,
            permisos__grupo__in=grupos_usuario,
            permisos__puede_autoasignar=True
        ).distinct()
        
        # Solicitudes grupales (sin asignar)
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).order_by('-fecha_creacion')
        
        # === BANDEJA PERSONAL ===
        # Solicitudes asignadas al usuario
        solicitudes_personales = Solicitud.objects.filter(
            asignada_a=request.user
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).order_by('-fecha_ultima_actualizacion')
    
    # === MÉTRICAS ===
    # Total en bandeja grupal
    total_grupo = solicitudes_grupales.count()
    
    # Mis tareas
    mis_tareas = solicitudes_personales.count()
    
    # Calcular vencimientos
    ahora = timezone.now()
    
    # Solicitudes por vencer (próximas 24 horas)
    por_vencer = 0
    en_tiempo = 0
    
    todas_solicitudes = list(solicitudes_grupales) + list(solicitudes_personales)
    
    for solicitud in todas_solicitudes:
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_vencimiento = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            
            if fecha_vencimiento < ahora:
                # Ya vencida
                continue
            elif fecha_vencimiento <= ahora + timedelta(hours=24):
                # Por vencer en 24 horas
                por_vencer += 1
            else:
                # En tiempo
                en_tiempo += 1
    
    # Filtros
    filtro_pipeline = request.GET.get('pipeline', '')
    filtro_estado = request.GET.get('estado', '')
    
    if filtro_pipeline:
        solicitudes_grupales = solicitudes_grupales.filter(pipeline_id=filtro_pipeline)
        solicitudes_personales = solicitudes_personales.filter(pipeline_id=filtro_pipeline)
    
    if filtro_estado == 'vencidas':
        # Filtrar solo las vencidas
        solicitudes_vencidas_ids = []
        for solicitud in todas_solicitudes:
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                fecha_vencimiento = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
                if fecha_vencimiento < ahora:
                    solicitudes_vencidas_ids.append(solicitud.id)
        
        solicitudes_grupales = solicitudes_grupales.filter(id__in=solicitudes_vencidas_ids)
        solicitudes_personales = solicitudes_personales.filter(id__in=solicitudes_vencidas_ids)
    
    # Agregar información de vencimiento y enriquecimiento a cada solicitud
    def agregar_info_vencimiento(solicitudes):
        for solicitud in solicitudes:
            # Información de SLA
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                fecha_vencimiento = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
                solicitud.fecha_vencimiento = fecha_vencimiento
                solicitud.esta_vencida = fecha_vencimiento < ahora
                solicitud.por_vencer = fecha_vencimiento <= ahora + timedelta(hours=24)
                
                # Calcular SLA restante y color
                tiempo_total = solicitud.etapa_actual.sla.total_seconds()
                tiempo_transcurrido = (ahora - solicitud.fecha_ultima_actualizacion).total_seconds()
                segundos_restantes = tiempo_total - tiempo_transcurrido
                porcentaje_restante = (segundos_restantes / tiempo_total) * 100 if tiempo_total > 0 else 0
                
                abs_segundos = abs(int(segundos_restantes))
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    if horas > 0:
                        solicitud.sla_restante = f"-{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"-{minutos}m"
                    solicitud.sla_color = 'text-danger'
                elif porcentaje_restante > 40:
                    if horas > 0:
                        solicitud.sla_restante = f"{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"{minutos}m"
                    solicitud.sla_color = 'text-success'
                elif porcentaje_restante > 0:
                    if horas > 0:
                        solicitud.sla_restante = f"{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"{minutos}m"
                    solicitud.sla_color = 'text-warning'
                else:
                    if horas > 0:
                        solicitud.sla_restante = f"-{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"-{minutos}m"
                    solicitud.sla_color = 'text-danger'
            else:
                solicitud.fecha_vencimiento = None
                solicitud.esta_vencida = False
                solicitud.por_vencer = False
                solicitud.sla_restante = 'N/A'
                solicitud.sla_color = 'text-secondary'
            
            # Las propiedades del modelo ya están disponibles directamente
            # No es necesario asignar nada - cliente_nombre, cliente_cedula, etc. 
            # están disponibles automáticamente como propiedades del modelo
            
            # Debug temporal para verificar que las propiedades funcionan correctamente
            try:
                # Estas propiedades se pueden leer sin problema
                _ = solicitud.cliente_nombre
                _ = solicitud.cliente_cedula
                _ = solicitud.monto_formateado
                _ = solicitud.producto_descripcion
            except Exception as e:
                print(f"Error accediendo propiedades del modelo: {e}")
            
            # Estado actual
            solicitud.estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            
        return solicitudes
    
    solicitudes_grupales = agregar_info_vencimiento(solicitudes_grupales)
    solicitudes_personales = agregar_info_vencimiento(solicitudes_personales)
    
    # Obtener datos únicos para los filtros
    todas_solicitudes_para_filtros = list(solicitudes_grupales) + list(solicitudes_personales)
    
    clientes_unicos = set()
    estados_unicos = set()
    etapas_unicas = set()
    
    for solicitud in todas_solicitudes_para_filtros:
        if hasattr(solicitud, 'cliente_nombre') and solicitud.cliente_nombre:
            clientes_unicos.add(solicitud.cliente_nombre)
        if hasattr(solicitud, 'estado_actual') and solicitud.estado_actual:
            estados_unicos.add(solicitud.estado_actual)
        if solicitud.etapa_actual:
            etapas_unicas.add(solicitud.etapa_actual.nombre)
    
    # Convertir a listas ordenadas
    clientes_unicos = sorted(list(clientes_unicos))
    estados_unicos = sorted(list(estados_unicos))
    etapas_unicas = sorted(list(etapas_unicas))
    
    # Obtener todas las etapas con bandeja habilitada (para el dropdown)
    etapas_con_bandeja = Etapa.objects.filter(es_bandeja_grupal=True).select_related('pipeline')
    
    context = {
        'solicitudes_grupales': solicitudes_grupales,
        'solicitudes_personales': solicitudes_personales,
        'total_grupo': total_grupo,
        'mis_tareas': mis_tareas,
        'por_vencer': por_vencer,
        'en_tiempo': en_tiempo,
        'pipelines': Pipeline.objects.all(),
        'clientes_unicos': clientes_unicos,
        'estados_unicos': estados_unicos,
        'etapas_unicas': etapas_unicas,
        'etapas_con_bandeja': etapas_con_bandeja,
        'filtros': {
            'pipeline': filtro_pipeline,
            'estado': filtro_estado,
        }
    }
    
    return render(request, 'workflow/vista_mixta_bandejas.html', context)


@login_required
def api_tomar_solicitud(request, solicitud_id):
    """API para tomar una solicitud de bandeja grupal"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar que la solicitud está en bandeja grupal
        if not solicitud.etapa_actual.es_bandeja_grupal or solicitud.asignada_a:
            return JsonResponse({
                'success': False, 
                'error': 'Esta solicitud no está disponible para tomar.'
            })
        
        # === SISTEMA DE PERMISOS SUPER STAFF ===
        # Los usuarios super staff (is_staff=True) pueden tomar cualquier solicitud
        if request.user.is_staff:
            # Super staff tiene permisos completos
            tiene_permiso = True
        else:
            # Verificar permisos regulares para usuarios normales
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_autoasignar=True
            ).exists()
        
        if not tiene_permiso:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para tomar solicitudes en esta etapa.'
            })
        
        # Asignar solicitud
        solicitud.asignada_a = request.user
        solicitud.fecha_ultima_actualizacion = timezone.now()
        solicitud.save()
        
        # Actualizar historial
        historial_actual = HistorialSolicitud.objects.filter(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            fecha_fin__isnull=True
        ).first()
        
        if historial_actual:
            historial_actual.usuario_responsable = request.user
            historial_actual.save()
        
        # CRÍTICO: Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'solicitud_tomada', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Solicitud {solicitud.codigo} asignada exitosamente.',
            'solicitud': {
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'asignada_a': request.user.get_full_name() or request.user.username
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_devolver_solicitud(request, solicitud_id):
    """API para devolver una solicitud a bandeja grupal"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # === SISTEMA DE PERMISOS SUPER STAFF ===
        # Los usuarios super staff (is_staff=True) pueden devolver cualquier solicitud
        if request.user.is_staff:
            # Super staff tiene permisos completos
            puede_devolver = True
        elif request.user.is_superuser:
            # Superuser también puede devolver cualquier solicitud
            puede_devolver = True
        elif solicitud.asignada_a == request.user:
            # Usuario regular solo puede devolver sus propias solicitudes
            puede_devolver = True
        else:
            puede_devolver = False
        
        if not puede_devolver:
            return JsonResponse({
                'success': False,
                'error': 'No puedes devolver esta solicitud.'
            })
        
        # Verificar que la etapa actual permite bandeja grupal
        if not solicitud.etapa_actual.es_bandeja_grupal:
            return JsonResponse({
                'success': False,
                'error': 'Esta etapa no permite bandeja grupal.'
            })
        
        # Devolver a bandeja grupal
        solicitud.asignada_a = None
        solicitud.fecha_ultima_actualizacion = timezone.now()
        solicitud.save()
        
        # CRÍTICO: Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'solicitud_devuelta', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Solicitud {solicitud.codigo} devuelta a bandeja grupal.',
            'solicitud': {
                'id': solicitud.id,
                'codigo': solicitud.codigo
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_kpis(request):
    """API para obtener KPIs actualizados"""
    try:
        # Obtener solicitudes del usuario
        solicitudes_usuario = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'cliente')
        
        # Calcular métricas
        total_grupo = solicitudes_usuario.filter(
            etapa_actual__es_bandeja_grupal=True,
            asignada_a__isnull=True
        ).count()
        
        mis_tareas = solicitudes_usuario.filter(
            asignada_a=request.user
        ).count()
        
        # Calcular por vencer y en tiempo
        por_vencer = 0
        en_tiempo = 0
        
        def calcular_sla_solicitud(solicitud):
            """Calcular SLA para una solicitud específica"""
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                
                if segundos_restantes < 0:
                    return 'text-danger'
                elif porcentaje_restante > 40:
                    return 'text-success'
                elif porcentaje_restante > 0:
                    return 'text-warning'
                else:
                    return 'text-danger'
            return 'text-secondary'
        
        for solicitud in solicitudes_usuario:
            sla_color = calcular_sla_solicitud(solicitud)
            if sla_color == 'text-warning':
                por_vencer += 1
            elif sla_color == 'text-success':
                en_tiempo += 1
        
        return JsonResponse({
            'success': True,
            'total_grupo': total_grupo,
            'mis_tareas': mis_tareas,
            'por_vencer': por_vencer,
            'en_tiempo': en_tiempo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def api_bandejas(request):
    """API para obtener contenido actualizado de las bandejas"""
    try:
        # Obtener solicitudes del usuario
        solicitudes_usuario = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'cliente')
        
        # Bandeja grupal
        bandeja_grupal = solicitudes_usuario.filter(
            etapa_actual__es_bandeja_grupal=True,
            asignada_a__isnull=True
        ).order_by('-fecha_creacion')
        
        # Bandeja personal
        bandeja_personal = solicitudes_usuario.filter(
            asignada_a=request.user
        ).order_by('-fecha_creacion')
        
        def generar_info_solicitud(solicitud):
            """Generar información completa de una solicitud"""
            info = {
                'cliente_nombre': 'Sin cliente',
                'cliente_cedula': 'Sin cédula',
                'sla_color': 'text-secondary',
                'tiempo_restante': 'N/A'
            }
            
            # Información de cliente
            try:
                from pacifico.models import Cotizacion
                cotizacion = Cotizacion.objects.filter(
                    solicitud_workflow=solicitud
                ).first()
                
                if cotizacion:
                    info['cliente_nombre'] = cotizacion.cliente or 'Sin cliente'
                    info['cliente_cedula'] = cotizacion.cedulaCliente or 'Sin cédula'
            except:
                pass
            
            # Información de SLA
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                abs_segundos = abs(segundos_restantes)
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    info['sla_color'] = 'text-danger'
                elif porcentaje_restante > 40:
                    info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    info['sla_color'] = 'text-success'
                elif porcentaje_restante > 0:
                    info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    info['sla_color'] = 'text-warning'
                else:
                    info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    info['sla_color'] = 'text-danger'
            
            return info
        
        # Generar HTML para bandeja grupal
        html_grupal = ""
        for solicitud in bandeja_grupal:
            info = generar_info_solicitud(solicitud)
            estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            
            html_grupal += f"""
            <tr class="solicitud-row" data-cliente="{info['cliente_nombre']}" 
                data-estado="{estado_actual}" 
                data-etapa="{solicitud.etapa_actual.nombre}" 
                data-sla="{info['sla_color']}" 
                data-search="{solicitud.codigo} {info['cliente_nombre']} {info['cliente_cedula']}"
                id="solicitud-grupal-{solicitud.id}">
                <td>
                    <span class="badge bg-primary">{solicitud.codigo}</span>
                </td>
                <td>{info['cliente_nombre']}</td>
                <td>{info['cliente_cedula']}</td>
                <td>
                    <span class="badge bg-info">{solicitud.etapa_actual.nombre}</span>
                </td>
                <td>
                    <i class="fas fa-circle {info['sla_color']} me-1"></i>
                    {info['tiempo_restante']}
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-success btn-sm tomar-solicitud" 
                                data-solicitud-id="{solicitud.id}" 
                                data-codigo="{solicitud.codigo}">
                            <i class="fas fa-hand-paper me-1"></i>Tomar
                        </button>
                        <button class="btn btn-info btn-sm ver-detalle" 
                                data-solicitud-id="{solicitud.id}">
                            <i class="fas fa-eye me-1"></i>Ver
                        </button>
                    </div>
                </td>
            </tr>
            """
        
        # Generar HTML para bandeja personal
        html_personal = ""
        for solicitud in bandeja_personal:
            info = generar_info_solicitud(solicitud)
            estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            
            html_personal += f"""
            <tr class="solicitud-row" data-cliente="{info['cliente_nombre']}" 
                data-estado="{estado_actual}" 
                data-etapa="{solicitud.etapa_actual.nombre}" 
                data-sla="{info['sla_color']}" 
                data-search="{solicitud.codigo} {info['cliente_nombre']} {info['cliente_cedula']}"
                id="solicitud-personal-{solicitud.id}">
                <td>
                    <span class="badge bg-primary">{solicitud.codigo}</span>
                </td>
                <td>{info['cliente_nombre']}</td>
                <td>{info['cliente_cedula']}</td>
                <td>
                    <span class="badge bg-info">{solicitud.etapa_actual.nombre}</span>
                </td>
                <td>
                    <i class="fas fa-circle {info['sla_color']} me-1"></i>
                    {info['tiempo_restante']}
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-warning btn-sm devolver-solicitud" 
                                data-solicitud-id="{solicitud.id}" 
                                data-codigo="{solicitud.codigo}">
                            <i class="fas fa-undo me-1"></i>Devolver
                        </button>
                        <button class="btn btn-primary btn-sm procesar-solicitud" 
                                data-solicitud-id="{solicitud.id}">
                            <i class="fas fa-cogs me-1"></i>Procesar
                        </button>
                        <button class="btn btn-info btn-sm ver-detalle" 
                                data-solicitud-id="{solicitud.id}">
                            <i class="fas fa-eye me-1"></i>Ver
                        </button>
                    </div>
                </td>
            </tr>
            """
        
        return JsonResponse({
            'success': True,
            'bandeja_grupal': html_grupal,
            'bandeja_personal': html_personal
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def test_envio_correo_bandeja(request):
    """
    Vista temporal para probar el envío de correos de bandeja grupal.
    Usar solo para testing - eliminar después.
    """
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        if solicitud_id:
            try:
                solicitud = Solicitud.objects.get(id=solicitud_id)
                etapa = solicitud.etapa_actual
                
                if etapa and etapa.es_bandeja_grupal:
                    enviar_correo_bandeja_grupal(solicitud, etapa)
                    return JsonResponse({
                        'success': True,
                        'message': f'Correo enviado para solicitud {solicitud.codigo}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'La etapa actual no es bandeja grupal'
                    })
            except Solicitud.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Solicitud no encontrada'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
    
    # Listar solicitudes para testing
    solicitudes = Solicitud.objects.filter(etapa_actual__es_bandeja_grupal=True)[:10]
    
    return render(request, 'workflow/test_correo.html', {
        'solicitudes': solicitudes
    })


@login_required
def api_get_updated_solicitudes(request):
    """API para obtener solo las solicitudes que han sido actualizadas"""
    try:
        # Obtener timestamp de la última consulta
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        view_type = request.GET.get('view', 'bandejas')
        
        # Obtener solicitudes actualizadas
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all(),
            fecha_ultima_actualizacion__gt=last_check_time
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Formatear datos según la vista
        solicitudes_data = []
        
        for solicitud in solicitudes_base:
            # Información de cliente
            cliente_nombre = 'Sin cliente'
            cliente_cedula = 'Sin cédula'
            
            try:
                from pacifico.models import Cotizacion
                cotizacion = Cotizacion.objects.filter(
                    solicitud_workflow=solicitud
                ).first()
                
                if cotizacion:
                    cliente_nombre = cotizacion.cliente or 'Sin cliente'
                    cliente_cedula = cotizacion.cedulaCliente or 'Sin cédula'
            except:
                pass
            
            # Calcular SLA
            sla_info = {
                'color': 'text-secondary',
                'tiempo_restante': 'N/A'
            }
            
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                abs_segundos = abs(segundos_restantes)
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
                elif porcentaje_restante > 40:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-success'
                elif porcentaje_restante > 0:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-warning'
                else:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
            
            solicitudes_data.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'cliente_cedula': cliente_cedula,
                'etapa': {
                    'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                    'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                    'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
                },
                'asignada_a': {
                    'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                    'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                    'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
                },
                'estado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else "En Proceso",
                'sla': sla_info,
                'fecha_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
                'fecha_creacion': solicitud.fecha_creacion.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'solicitudes': solicitudes_data,
            'total': len(solicitudes_data),
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': view_type
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })


@login_required
def api_solicitud_brief(request, solicitud_id):
    """API: Briefing de una solicitud para el modal"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)

        # General info
        general = {
            'codigo': solicitud.codigo,
            'estado': solicitud.subestado_actual.nombre if solicitud.subestado_actual else (solicitud.etapa_actual.nombre if solicitud.etapa_actual else '-'),
            'tipo': solicitud.pipeline.nombre if solicitud.pipeline else '-',
            'fecha_inicio': solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_creacion else '-',
            'vencimiento': solicitud.historial.last().fecha_fin.strftime('%d/%m/%Y') if solicitud.historial.last() and solicitud.historial.last().fecha_fin else '-',
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else '-',
            'area': '-',  # Campo no existe en el modelo, usar valor por defecto
        }

        # Cliente info
        cliente = solicitud.cliente
        cliente_info = {
            'nombre': cliente.nombreCliente if cliente else '-',
            'cedula': cliente.cedulaCliente if cliente else '-',
            'canal': '-',  # Campo no existe en el modelo, usar valor por defecto
        }

        # Acciones (permisos y flags)
        acciones = {
            'puede_procesar': True,  # TODO: lógica de permisos
            'puede_devolver': True,
            'puede_anular': True,
            'puede_comentar': True,
        }

        # Workflow progress (etapas)
        workflow = []
        if solicitud.pipeline:
            etapas = solicitud.pipeline.etapas.order_by('orden')
            for etapa in etapas:
                # Calcular SLA en días desde el campo sla (DurationField)
                sla_dias = None
                if etapa.sla:
                    sla_dias = etapa.sla.days
                
                etapa_dict = {
                    'nombre': etapa.nombre,
                    'completada': solicitud.historial.filter(etapa=etapa, fecha_fin__isnull=False).exists(),
                    'actual': solicitud.etapa_actual_id == etapa.id,
                    'responsable': '-',  # Campo no existe en el modelo
                    'sla': f"{sla_dias} días" if sla_dias else None
                }
                workflow.append(etapa_dict)

        # Historial
        historial = [
            {
                'etapa': h.etapa.nombre if h.etapa else '-',
                'subestado': h.subestado.nombre if h.subestado else '-',
                'usuario': h.usuario_responsable.get_full_name() if h.usuario_responsable else '-',
                'fecha_inicio': h.fecha_inicio.strftime('%d/%m/%Y %H:%M') if h.fecha_inicio else '-',
                'fecha_fin': h.fecha_fin.strftime('%d/%m/%Y %H:%M') if h.fecha_fin else None,
            }
            for h in solicitud.historial.all().order_by('fecha_inicio')
        ]

        # Comentarios
        comentarios = []
        if hasattr(solicitud, 'comentarios'):
            comentarios = [
                {
                    'usuario': c.usuario.get_full_name() if c.usuario else '-',
                    'texto': c.comentario,  # Campo correcto del modelo
                    'fecha': c.fecha_creacion.strftime('%d/%m/%Y %H:%M') if c.fecha_creacion else '-',
                }
                for c in solicitud.comentarios.all().order_by('-fecha_creacion')
            ]

        return JsonResponse({
            'general': general,
            'cliente': cliente_info,
            'acciones': acciones,
            'workflow': workflow,
            'historial': historial,
            'comentarios': comentarios,
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos de la solicitud: {str(e)}'
        }, status=500)


# ==========================================
# VISTAS DE API PARA COMENTARIOS
# ==========================================

@login_required
def api_obtener_comentarios(request, solicitud_id):
    """API para obtener comentarios de una solicitud"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos para ver la solicitud
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        comentarios = solicitud.comentarios.all().order_by('-fecha_creacion')
        
        datos_comentarios = []
        for comentario in comentarios:
            datos_comentarios.append({
                'id': comentario.id,
                'usuario': {
                    'id': comentario.usuario.id,
                    'username': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username
                },
                'comentario': comentario.comentario,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat(),
                'es_editado': comentario.es_editado,
                'tiempo_transcurrido': comentario.get_tiempo_transcurrido(),
                'puede_editar': comentario.usuario == request.user or request.user.is_superuser,
                'puede_eliminar': comentario.usuario == request.user or request.user.is_superuser
            })
        
        return JsonResponse({
            'success': True,
            'comentarios': datos_comentarios,
            'total': len(datos_comentarios)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_crear_comentario(request, solicitud_id):
    """API para crear un nuevo comentario"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos para comentar en la solicitud
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({'error': 'No tienes permisos para comentar en esta solicitud'}, status=403)
        
        data = json.loads(request.body)
        comentario_texto = data.get('comentario', '').strip()
        
        if not comentario_texto:
            return JsonResponse({'error': 'El comentario no puede estar vacío'}, status=400)
        
        # Crear el comentario
        comentario = SolicitudComentario.objects.create(
            solicitud=solicitud,
            usuario=request.user,
            comentario=comentario_texto
        )
        
        # Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'nuevo_comentario', request.user)
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': comentario.id,
                'usuario': {
                    'id': comentario.usuario.id,
                    'username': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username
                },
                'comentario': comentario.comentario,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat(),
                'es_editado': comentario.es_editado,
                'tiempo_transcurrido': comentario.get_tiempo_transcurrido(),
                'puede_editar': True,
                'puede_eliminar': True
            },
            'mensaje': 'Comentario creado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_editar_comentario(request, comentario_id):
    """API para editar un comentario existente"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        comentario = get_object_or_404(SolicitudComentario, id=comentario_id)
        
        # Verificar permisos para editar el comentario
        if not (comentario.usuario == request.user or request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para editar este comentario'}, status=403)
        
        data = json.loads(request.body)
        nuevo_comentario = data.get('comentario', '').strip()
        
        if not nuevo_comentario:
            return JsonResponse({'error': 'El comentario no puede estar vacío'}, status=400)
        
        # Actualizar el comentario
        comentario.comentario = nuevo_comentario
        comentario.save()
        
        # Notificar cambio en tiempo real
        notify_solicitud_change(comentario.solicitud, 'comentario_editado', request.user)
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': comentario.id,
                'usuario': {
                    'id': comentario.usuario.id,
                    'username': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username
                },
                'comentario': comentario.comentario,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat(),
                'es_editado': comentario.es_editado,
                'tiempo_transcurrido': comentario.get_tiempo_transcurrido(),
                'puede_editar': True,
                'puede_eliminar': True
            },
            'mensaje': 'Comentario actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_eliminar_comentario(request, comentario_id):
    """API para eliminar un comentario"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        comentario = get_object_or_404(SolicitudComentario, id=comentario_id)
        
        # Verificar permisos para eliminar el comentario
        if not (comentario.usuario == request.user or request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para eliminar este comentario'}, status=403)
        
        solicitud = comentario.solicitud
        comentario.delete()
        
        # Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'comentario_eliminado', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Comentario eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# VISTAS DE API PARA SOLICITUDES ACTUALIZADAS
# ==========================================

@login_required
def api_get_updated_solicitudes(request):
    """API para obtener solo las solicitudes que han sido actualizadas"""
    try:
        # Obtener timestamp de la última consulta
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        view_type = request.GET.get('view', 'bandejas')
        
        # Obtener solicitudes actualizadas
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all(),
            fecha_ultima_actualizacion__gt=last_check_time
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Formatear datos según la vista
        solicitudes_data = []
        
        for solicitud in solicitudes_base:
            # Información de cliente
            cliente_nombre = 'Sin cliente'
            cliente_cedula = 'Sin cédula'
            
            try:
                from pacifico.models import Cotizacion
                cotizacion = Cotizacion.objects.filter(
                    solicitud_workflow=solicitud
                ).first()
                
                if cotizacion:
                    cliente_nombre = cotizacion.cliente or 'Sin cliente'
                    cliente_cedula = cotizacion.cedulaCliente or 'Sin cédula'
            except:
                pass
            
            # Calcular SLA
            sla_info = {
                'color': 'text-secondary',
                'tiempo_restante': 'N/A'
            }
            
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                abs_segundos = abs(segundos_restantes)
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
                elif porcentaje_restante > 40:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-success'
                elif porcentaje_restante > 0:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-warning'
                else:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
            
            solicitudes_data.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'cliente_cedula': cliente_cedula,
                'etapa': {
                    'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                    'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                    'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
                },
                'asignada_a': {
                    'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                    'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                    'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
                },
                'estado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else "En Proceso",
                'sla': sla_info,
                'fecha_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
                'fecha_creacion': solicitud.fecha_creacion.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'solicitudes': solicitudes_data,
            'total': len(solicitudes_data),
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': view_type
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })


@login_required
def api_obtener_requisitos_transicion(request, solicitud_id):
    """API para obtener requisitos faltantes de una transición específica"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        nueva_etapa_id = request.GET.get('nueva_etapa_id')
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de nueva etapa requerido'}, status=400)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Buscar transición
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if not transicion:
            return JsonResponse({
                'success': True,
                'requisitos_faltantes': [],
                'mensaje': 'No hay requisitos especiales para esta transición'
            })
        
        # Obtener requisitos faltantes
        requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
        
        return JsonResponse({
            'success': True,
            'requisitos_faltantes': requisitos_faltantes,
            'transicion': {
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': transicion.etapa_origen.nombre,
                'etapa_destino': transicion.etapa_destino.nombre
            },
            'total_faltantes': len(requisitos_faltantes)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_subir_requisito_transicion(request, solicitud_id):
    """API para subir un archivo de requisito faltante"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        requisito_id = request.POST.get('requisito_id')
        
        if not requisito_id:
            return JsonResponse({'error': 'ID de requisito requerido'}, status=400)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para modificar esta solicitud'}, status=403)
        
        requisito = get_object_or_404(Requisito, id=requisito_id)
        
        # Verificar que hay un archivo
        if 'archivo' not in request.FILES:
            return JsonResponse({'error': 'No se proporcionó ningún archivo'}, status=400)
        
        archivo = request.FILES['archivo']
        
        # Obtener o crear RequisitoSolicitud
        requisito_solicitud, created = RequisitoSolicitud.objects.get_or_create(
            solicitud=solicitud,
            requisito=requisito,
            defaults={
                'cumplido': True,
                'observaciones': f'Archivo subido por {request.user.get_full_name() or request.user.username} el {timezone.now().strftime("%d/%m/%Y %H:%M")}'
            }
        )
        
        # Actualizar archivo y marcar como cumplido
        requisito_solicitud.archivo = archivo
        requisito_solicitud.cumplido = True
        if not created:
            # Actualizar observaciones si ya existía
            requisito_solicitud.observaciones += f'\nActualizado por {request.user.get_full_name() or request.user.username} el {timezone.now().strftime("%d/%m/%Y %H:%M")}'
        
        requisito_solicitud.save()
        
        # Notificar cambio
        notify_solicitud_change(solicitud, 'requisito_actualizado', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Archivo para "{requisito.nombre}" subido exitosamente',
            'requisito': {
                'id': requisito.id,
                'nombre': requisito.nombre,
                'archivo_url': requisito_solicitud.archivo.url if requisito_solicitud.archivo else None,
                'cumplido': requisito_solicitud.cumplido
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_validar_requisitos_antes_transicion(request, solicitud_id):
    """API para validar requisitos antes de realizar una transición"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        nueva_etapa_id = request.GET.get('nueva_etapa_id')
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de nueva etapa requerido'}, status=400)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Buscar transición
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if not transicion:
            return JsonResponse({
                'success': True,
                'puede_continuar': True,
                'mensaje': 'No hay requisitos especiales para esta transición'
            })
        
        # Verificar requisitos
        requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
        
        return JsonResponse({
            'success': True,
            'puede_continuar': len(requisitos_faltantes) == 0,
            'requisitos_faltantes': requisitos_faltantes,
            'total_faltantes': len(requisitos_faltantes),
            'mensaje': 'Todos los requisitos están completos' if len(requisitos_faltantes) == 0 else f'Faltan {len(requisitos_faltantes)} requisito(s)'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# VISTAS DE API PARA REQUISITOS DE TRANSICIÓN
# ==========================================

@login_required
@permission_required('workflow.add_requisitotransicion')
def api_obtener_requisitos_transicion_pipeline(request, pipeline_id):
    """API para obtener todos los requisitos de transición de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Obtener todas las transiciones del pipeline
        transiciones = TransicionEtapa.objects.filter(pipeline=pipeline).select_related(
            'etapa_origen', 'etapa_destino'
        )
        
        # Obtener requisitos de transición
        requisitos_transicion = RequisitoTransicion.objects.filter(
            transicion__pipeline=pipeline
        ).select_related('transicion', 'requisito', 'transicion__etapa_origen', 'transicion__etapa_destino')
        
        # Formatear datos para el frontend
        datos_transiciones = []
        for transicion in transiciones:
            requisitos_de_transicion = [
                {
                    'id': rt.id,
                    'requisito_id': rt.requisito.id,
                    'requisito_nombre': rt.requisito.nombre,
                    'obligatorio': rt.obligatorio,
                    'mensaje_personalizado': rt.mensaje_personalizado or ''
                }
                for rt in requisitos_transicion if rt.transicion_id == transicion.id
            ]
            
            datos_transiciones.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': {
                    'id': transicion.etapa_origen.id,
                    'nombre': transicion.etapa_origen.nombre
                },
                'etapa_destino': {
                    'id': transicion.etapa_destino.id,
                    'nombre': transicion.etapa_destino.nombre
                },
                'requisitos': requisitos_de_transicion
            })
        
        # Obtener solo los requisitos asignados a este pipeline
        requisitos_disponibles = Requisito.objects.filter(
            requisitopipeline__pipeline=pipeline
        ).values('id', 'nombre', 'descripcion').distinct()
        
        return JsonResponse({
            'success': True,
            'transiciones': datos_transiciones,
            'requisitos_disponibles': list(requisitos_disponibles)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('workflow.add_requisitotransicion')
def api_crear_requisito_transicion(request):
    """API para crear un requisito de transición"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        transicion_id = data.get('transicion_id')
        requisito_id = data.get('requisito_id')
        obligatorio = data.get('obligatorio', True)
        mensaje_personalizado = data.get('mensaje_personalizado', '')
        
        if not all([transicion_id, requisito_id]):
            return JsonResponse({'error': 'Transición y requisito son obligatorios'}, status=400)
        
        transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
        requisito = get_object_or_404(Requisito, id=requisito_id)
        
        # Verificar que no existe ya esta combinación
        if RequisitoTransicion.objects.filter(transicion=transicion, requisito=requisito).exists():
            return JsonResponse({'error': 'Este requisito ya está asignado a esta transición'}, status=400)
        
        # Crear el requisito de transición
        requisito_transicion = RequisitoTransicion.objects.create(
            transicion=transicion,
            requisito=requisito,
            obligatorio=obligatorio,
            mensaje_personalizado=mensaje_personalizado
        )
        
        return JsonResponse({
            'success': True,
            'requisito_transicion': {
                'id': requisito_transicion.id,
                'transicion_id': transicion.id,
                'transicion_nombre': transicion.nombre,
                'requisito_id': requisito.id,
                'requisito_nombre': requisito.nombre,
                'obligatorio': requisito_transicion.obligatorio,
                'mensaje_personalizado': requisito_transicion.mensaje_personalizado
            },
            'mensaje': f'Requisito "{requisito.nombre}" asignado a la transición "{transicion.nombre}"'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@permission_required('workflow.change_requisitotransicion')
def api_actualizar_requisito_transicion(request, requisito_transicion_id):
    """API para actualizar un requisito de transición"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        requisito_transicion = get_object_or_404(RequisitoTransicion, id=requisito_transicion_id)
        
        data = json.loads(request.body)
        obligatorio = data.get('obligatorio', requisito_transicion.obligatorio)
        mensaje_personalizado = data.get('mensaje_personalizado', requisito_transicion.mensaje_personalizado)
        
        # Actualizar campos
        requisito_transicion.obligatorio = obligatorio
        requisito_transicion.mensaje_personalizado = mensaje_personalizado
        requisito_transicion.save()
        
        return JsonResponse({
            'success': True,
            'requisito_transicion': {
                'id': requisito_transicion.id,
                'obligatorio': requisito_transicion.obligatorio,
                'mensaje_personalizado': requisito_transicion.mensaje_personalizado
            },
            'mensaje': 'Requisito de transición actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@permission_required('workflow.delete_requisitotransicion')
def api_eliminar_requisito_transicion(request, requisito_transicion_id):
    """API para eliminar un requisito de transición"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        requisito_transicion = get_object_or_404(RequisitoTransicion, id=requisito_transicion_id)
        
        transicion_nombre = requisito_transicion.transicion.nombre
        requisito_nombre = requisito_transicion.requisito.nombre
        
        requisito_transicion.delete()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Requisito "{requisito_nombre}" removido de la transición "{transicion_nombre}"'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# APIs PARA GESTIÓN DE PERMISOS DE PIPELINE
# ==========================================

@login_required
@permission_required('workflow.add_permisopipeline')
def api_obtener_permisos_pipeline(request, pipeline_id):
    """API para obtener permisos de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        permisos = PermisoPipeline.objects.filter(pipeline=pipeline).select_related('grupo', 'usuario')
        
        permisos_data = []
        for permiso in permisos:
            permisos_data.append({
                'id': permiso.id,
                'grupo': {
                    'id': permiso.grupo.id,
                    'name': permiso.grupo.name
                } if permiso.grupo else None,
                'usuario': {
                    'id': permiso.usuario.id,
                    'username': permiso.usuario.username,
                    'first_name': permiso.usuario.first_name,
                    'last_name': permiso.usuario.last_name
                } if permiso.usuario else None,
                'puede_ver': permiso.puede_ver,
                'puede_crear': permiso.puede_crear,
                'puede_editar': permiso.puede_editar,
                'puede_eliminar': permiso.puede_eliminar,
                'puede_admin': permiso.puede_admin
            })
        
        return JsonResponse({
            'success': True,
            'permisos': permisos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('workflow.add_permisopipeline')
def api_crear_permiso_pipeline(request, pipeline_id):
    """API para crear un permiso de pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            data = json.loads(request.body)
            
            grupo_id = data.get('grupo_id')
            usuario_id = data.get('usuario_id')
            
            if not grupo_id and not usuario_id:
                return JsonResponse({'success': False, 'error': 'Debe especificar un grupo o un usuario'})
            
            if grupo_id and usuario_id:
                return JsonResponse({'success': False, 'error': 'No puede especificar tanto un grupo como un usuario'})
            
            # Verificar si ya existe el permiso
            if grupo_id:
                grupo = get_object_or_404(Group, id=grupo_id)
                permiso, created = PermisoPipeline.objects.get_or_create(
                    pipeline=pipeline,
                    grupo=grupo,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_crear': data.get('puede_crear', False),
                        'puede_editar': data.get('puede_editar', False),
                        'puede_eliminar': data.get('puede_eliminar', False),
                        'puede_admin': data.get('puede_admin', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_crear = data.get('puede_crear', False)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.puede_eliminar = data.get('puede_eliminar', False)
                    permiso.puede_admin = data.get('puede_admin', False)
                    permiso.save()
            else:
                usuario = get_object_or_404(User, id=usuario_id)
                permiso, created = PermisoPipeline.objects.get_or_create(
                    pipeline=pipeline,
                    usuario=usuario,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_crear': data.get('puede_crear', False),
                        'puede_editar': data.get('puede_editar', False),
                        'puede_eliminar': data.get('puede_eliminar', False),
                        'puede_admin': data.get('puede_admin', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_crear = data.get('puede_crear', False)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.puede_eliminar = data.get('puede_eliminar', False)
                    permiso.puede_admin = data.get('puede_admin', False)
                    permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso creado/actualizado exitosamente',
                'permiso': {
                    'id': permiso.id,
                    'grupo': {
                        'id': permiso.grupo.id,
                        'name': permiso.grupo.name
                    } if permiso.grupo else None,
                    'usuario': {
                        'id': permiso.usuario.id,
                        'username': permiso.usuario.username,
                        'first_name': permiso.usuario.first_name,
                        'last_name': permiso.usuario.last_name
                    } if permiso.usuario else None,
                    'puede_ver': permiso.puede_ver,
                    'puede_crear': permiso.puede_crear,
                    'puede_editar': permiso.puede_editar,
                    'puede_eliminar': permiso.puede_eliminar,
                    'puede_admin': permiso.puede_admin
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.change_permisopipeline')
def api_actualizar_permiso_pipeline(request, pipeline_id, permiso_id):
    """API para actualizar un permiso de pipeline"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoPipeline, id=permiso_id, pipeline_id=pipeline_id)
            data = json.loads(request.body)
            
            permiso.puede_ver = data.get('puede_ver', True)
            permiso.puede_crear = data.get('puede_crear', False)
            permiso.puede_editar = data.get('puede_editar', False)
            permiso.puede_eliminar = data.get('puede_eliminar', False)
            permiso.puede_admin = data.get('puede_admin', False)
            permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.delete_permisopipeline')
def api_eliminar_permiso_pipeline(request, pipeline_id, permiso_id):
    """API para eliminar un permiso de pipeline"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoPipeline, id=permiso_id, pipeline_id=pipeline_id)
            permiso.delete()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ==========================================
# APIs PARA GESTIÓN DE PERMISOS DE BANDEJA
# ==========================================

@login_required
@permission_required('workflow.add_permisobandeja')
def api_obtener_permisos_bandeja(request, etapa_id):
    """API para obtener permisos de una bandeja (etapa)"""
    try:
        etapa = get_object_or_404(Etapa, id=etapa_id)
        permisos = PermisoBandeja.objects.filter(etapa=etapa).select_related('grupo', 'usuario')
        
        permisos_data = []
        for permiso in permisos:
            permisos_data.append({
                'id': permiso.id,
                'grupo': {
                    'id': permiso.grupo.id,
                    'name': permiso.grupo.name
                } if permiso.grupo else None,
                'usuario': {
                    'id': permiso.usuario.id,
                    'username': permiso.usuario.username,
                    'first_name': permiso.usuario.first_name,
                    'last_name': permiso.usuario.last_name
                } if permiso.usuario else None,
                'puede_ver': permiso.puede_ver,
                'puede_tomar': permiso.puede_tomar,
                'puede_devolver': permiso.puede_devolver,
                'puede_transicionar': permiso.puede_transicionar,
                'puede_editar': permiso.puede_editar
            })
        
        return JsonResponse({
            'success': True,
            'permisos': permisos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('workflow.add_permisobandeja')
def api_crear_permiso_bandeja(request, etapa_id):
    """API para crear un permiso de bandeja"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            data = json.loads(request.body)
            
            grupo_id = data.get('grupo_id')
            usuario_id = data.get('usuario_id')
            
            if not grupo_id and not usuario_id:
                return JsonResponse({'success': False, 'error': 'Debe especificar un grupo o un usuario'})
            
            if grupo_id and usuario_id:
                return JsonResponse({'success': False, 'error': 'No puede especificar tanto un grupo como un usuario'})
            
            # Verificar si ya existe el permiso
            if grupo_id:
                grupo = get_object_or_404(Group, id=grupo_id)
                permiso, created = PermisoBandeja.objects.get_or_create(
                    etapa=etapa,
                    grupo=grupo,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_tomar': data.get('puede_tomar', True),
                        'puede_devolver': data.get('puede_devolver', True),
                        'puede_transicionar': data.get('puede_transicionar', True),
                        'puede_editar': data.get('puede_editar', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_tomar = data.get('puede_tomar', True)
                    permiso.puede_devolver = data.get('puede_devolver', True)
                    permiso.puede_transicionar = data.get('puede_transicionar', True)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.save()
            else:
                usuario = get_object_or_404(User, id=usuario_id)
                permiso, created = PermisoBandeja.objects.get_or_create(
                    etapa=etapa,
                    usuario=usuario,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_tomar': data.get('puede_tomar', True),
                        'puede_devolver': data.get('puede_devolver', True),
                        'puede_transicionar': data.get('puede_transicionar', True),
                        'puede_editar': data.get('puede_editar', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_tomar = data.get('puede_tomar', True)
                    permiso.puede_devolver = data.get('puede_devolver', True)
                    permiso.puede_transicionar = data.get('puede_transicionar', True)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso creado/actualizado exitosamente',
                'permiso': {
                    'id': permiso.id,
                    'grupo': {
                        'id': permiso.grupo.id,
                        'name': permiso.grupo.name
                    } if permiso.grupo else None,
                    'usuario': {
                        'id': permiso.usuario.id,
                        'username': permiso.usuario.username,
                        'first_name': permiso.usuario.first_name,
                        'last_name': permiso.usuario.last_name
                    } if permiso.usuario else None,
                    'puede_ver': permiso.puede_ver,
                    'puede_tomar': permiso.puede_tomar,
                    'puede_devolver': permiso.puede_devolver,
                    'puede_transicionar': permiso.puede_transicionar,
                    'puede_editar': permiso.puede_editar
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.change_permisobandeja')
def api_actualizar_permiso_bandeja(request, etapa_id, permiso_id):
    """API para actualizar un permiso de bandeja"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoBandeja, id=permiso_id, etapa_id=etapa_id)
            data = json.loads(request.body)
            
            permiso.puede_ver = data.get('puede_ver', True)
            permiso.puede_tomar = data.get('puede_tomar', True)
            permiso.puede_devolver = data.get('puede_devolver', True)
            permiso.puede_transicionar = data.get('puede_transicionar', True)
            permiso.puede_editar = data.get('puede_editar', False)
            permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.delete_permisobandeja')
def api_eliminar_permiso_bandeja(request, etapa_id, permiso_id):
    """API para eliminar un permiso de bandeja"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoBandeja, id=permiso_id, etapa_id=etapa_id)
            permiso.delete()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ==========================================
# APIs PARA OBTENER USUARIOS Y GRUPOS
# ==========================================

@login_required
def api_obtener_usuarios(request):
    """API para obtener lista de usuarios activos"""
    try:
        usuarios = User.objects.filter(is_active=True).order_by('username')
        usuarios_data = []
        
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id,
                'username': usuario.username,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'email': usuario.email,
                'full_name': f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
            })
        
        return JsonResponse({
            'success': True,
            'usuarios': usuarios_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_obtener_grupos(request):
    """API para obtener lista de grupos"""
    try:
        grupos = Group.objects.all().order_by('name')
        grupos_data = []
        
        for grupo in grupos:
            grupos_data.append({
                'id': grupo.id,
                'name': grupo.name,
                'user_count': grupo.user_set.count()
            })
        
        return JsonResponse({
            'success': True,
            'grupos': grupos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# FUNCIONES PARA REQUISITOS DE TRANSICIÓN
# ==========================================
