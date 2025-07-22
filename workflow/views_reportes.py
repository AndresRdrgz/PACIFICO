from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F, Case, When, Sum, Max, Min, DurationField
from django.db.models.functions import Extract, Coalesce
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import pandas as pd
import io
from datetime import datetime, timedelta, date
from decimal import Decimal
import time
from functools import wraps

from .modelsWorkflow import (
    Pipeline, Etapa, SubEstado, TransicionEtapa, PermisoEtapa, 
    Solicitud, HistorialSolicitud, Requisito, RequisitoPipeline, 
    RequisitoSolicitud, CampoPersonalizado, ValorCampoSolicitud,
    RequisitoTransicion, SolicitudComentario, PermisoPipeline, PermisoBandeja,
    NivelComite, UsuarioNivelComite, ParticipacionComite, ReportePersonalizado,
    EjecucionReporte, CalificacionCampo
)
from pacifico.models import Cliente, Cotizacion

# ==========================================
# DECORADORES Y UTILIDADES
# ==========================================

def admin_or_supervisor_required(view_func):
    """
    Decorator que permite acceso solo a admin y supervisores
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Verificar si el usuario pertenece a grupos de supervisión
        grupos_supervisor = ['Supervisores', 'Gerencia', 'Administradores']
        if request.user.groups.filter(name__in=grupos_supervisor).exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('workflow:dashboard')
    
    return _wrapped_view

def medir_tiempo_ejecucion(func):
    """Decorator para medir tiempo de ejecución"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        resultado['tiempo_ejecucion'] = fin - inicio
        return resultado
    return wrapper

# ==========================================
# VISTA PRINCIPAL DE REPORTES
# ==========================================

@login_required
@admin_or_supervisor_required
def reportes_dashboard(request):
    """Dashboard principal de reportería con estadísticas y reportes guardados"""
    
    try:
        # Estadísticas básicas simples
        total_solicitudes = Solicitud.objects.count()
        solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
        solicitudes_completadas = total_solicitudes - solicitudes_activas
        solicitudes_vencidas = 0  # Simplificado por ahora
        
        # Reportes del usuario - simplificado
        reportes_usuario = []
        reportes_favoritos = []
        try:
            reportes_usuario = ReportePersonalizado.objects.filter(usuario=request.user)[:10]
            reportes_favoritos = ReportePersonalizado.objects.filter(
                usuario=request.user, es_favorito=True
            )[:5]
        except:
            pass
        
        # Estadísticas básicas
        stats_pipelines = []
        stats_etapas = []
        usuarios_activos = []
        
        try:
            # Stats de pipelines básicas
            for pipeline in Pipeline.objects.all()[:5]:
                total = Solicitud.objects.filter(pipeline=pipeline).count()
                activas = Solicitud.objects.filter(
                    pipeline=pipeline, etapa_actual__isnull=False
                ).count()
                stats_pipelines.append({
                    'nombre': pipeline.nombre,
                    'total_solicitudes': total,
                    'solicitudes_activas': activas
                })
            
            # Stats de etapas básicas
            for etapa in Etapa.objects.all()[:10]:
                actuales = Solicitud.objects.filter(etapa_actual=etapa).count()
                stats_etapas.append({
                    'nombre': etapa.nombre,
                    'pipeline__nombre': etapa.pipeline.nombre,
                    'solicitudes_actuales': actuales
                })
            
            # Usuarios activos básicos
            usuarios_activos = User.objects.filter(is_active=True)[:10]
        except:
            pass
        
        # Tendencias simples
        tendencias = []
        try:
            hace_30_dias = timezone.now() - timedelta(days=30)
            for i in range(7):  # Solo 7 días para simplificar
                fecha = (timezone.now() - timedelta(days=i)).date()
                count = Solicitud.objects.filter(fecha_creacion__date=fecha).count()
                tendencias.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'total': count
                })
            tendencias.reverse()
        except:
            tendencias = []
        
        context = {
            'total_solicitudes': total_solicitudes,
            'solicitudes_activas': solicitudes_activas,
            'solicitudes_completadas': solicitudes_completadas,
            'solicitudes_vencidas': solicitudes_vencidas,
            'reportes_usuario': reportes_usuario,
            'reportes_favoritos': reportes_favoritos,
            'stats_pipelines': stats_pipelines,
            'stats_etapas': stats_etapas,
            'usuarios_activos': usuarios_activos,
            'tendencias': tendencias,
            'pipelines': Pipeline.objects.all(),
            'etapas': Etapa.objects.all(),
            'usuarios': User.objects.filter(is_active=True).order_by('first_name', 'last_name'),
            'grupos': Group.objects.all()
        }
        
        return render(request, 'workflow/reportes.html', context)
        
    except Exception as e:
        # Si hay cualquier error, mostrar página básica
        context = {
            'total_solicitudes': 0,
            'solicitudes_activas': 0,
            'solicitudes_completadas': 0,
            'solicitudes_vencidas': 0,
            'reportes_usuario': [],
            'reportes_favoritos': [],
            'stats_pipelines': [],
            'stats_etapas': [],
            'usuarios_activos': [],
            'tendencias': [],
            'pipelines': Pipeline.objects.all(),
            'etapas': Etapa.objects.all(),
            'usuarios': User.objects.filter(is_active=True),
            'grupos': Group.objects.all(),
            'error_debug': str(e)
        }
        return render(request, 'workflow/reportes.html', context)

# ==========================================
# APIs PARA REPORTES
# ==========================================

@login_required
@admin_or_supervisor_required
@csrf_exempt
@require_http_methods(["POST"])
def api_crear_reporte(request):
    """API para crear un nuevo reporte personalizado"""
    try:
        data = json.loads(request.body)
        
        reporte = ReportePersonalizado.objects.create(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', ''),
            usuario=request.user,
            filtros_json=data.get('filtros', {}),
            campos_json=data.get('campos', []),
            configuracion_json=data.get('configuracion', {}),
            es_publico=data.get('es_publico', False)
        )
        
        # Agregar grupos si es público
        if reporte.es_publico and data.get('grupos_compartidos'):
            grupos = Group.objects.filter(id__in=data.get('grupos_compartidos'))
            reporte.grupos_compartidos.set(grupos)
        
        return JsonResponse({
            'success': True,
            'reporte_id': reporte.id,
            'message': 'Reporte creado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear reporte: {str(e)}'
        })

@login_required
@admin_or_supervisor_required
@medir_tiempo_ejecucion
def api_ejecutar_reporte(request, reporte_id):
    """API para ejecutar un reporte personalizado"""
    try:
        reporte = get_object_or_404(ReportePersonalizado, id=reporte_id)
        
        # Verificar permisos
        if not reporte.puede_ver(request.user):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para ejecutar este reporte'
            })
        
        # Obtener parámetros adicionales del request
        filtros_extra = {}
        if request.method == 'POST':
            filtros_extra = json.loads(request.body).get('filtros_extra', {})
        
        # Construir consulta base
        queryset = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a', 'cliente', 'cotizacion'
        ).prefetch_related('historial', 'comentarios', 'requisitos')
        
        # Aplicar filtros del reporte
        filtros = {**reporte.filtros_json, **filtros_extra}
        queryset = aplicar_filtros_reporte(queryset, filtros)
        
        # Obtener datos según los campos configurados
        datos = obtener_datos_reporte(queryset, reporte.campos_json, reporte.configuracion_json)
        
        # Marcar como ejecutado
        reporte.marcar_ejecutado()
        
        # Guardar ejecución
        EjecucionReporte.objects.create(
            reporte=reporte,
            usuario=request.user,
            parametros_json=filtros_extra,
            registros_resultantes=len(datos),
            exitosa=True
        )
        
        return JsonResponse({
            'success': True,
            'datos': datos,
            'total_registros': len(datos),
            'configuracion': reporte.configuracion_json
        })
        
    except Exception as e:
        # Guardar ejecución fallida
        EjecucionReporte.objects.create(
            reporte=reporte if 'reporte' in locals() else None,
            usuario=request.user,
            exitosa=False,
            mensaje_error=str(e)
        )
        
        return JsonResponse({
            'success': False,
            'message': f'Error al ejecutar reporte: {str(e)}'
        })

@login_required
@admin_or_supervisor_required
def api_exportar_reporte(request, reporte_id):
    """API para exportar un reporte a Excel"""
    try:
        reporte = get_object_or_404(ReportePersonalizado, id=reporte_id)
        
        # Verificar permisos
        if not reporte.puede_ver(request.user):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para exportar este reporte'
            })
        
        # Obtener parámetros adicionales
        filtros_extra = {}
        if request.method == 'POST':
            filtros_extra = json.loads(request.body).get('filtros_extra', {})
        
        # Construir consulta
        queryset = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a', 'cliente', 'cotizacion'
        )
        
        filtros = {**reporte.filtros_json, **filtros_extra}
        queryset = aplicar_filtros_reporte(queryset, filtros)
        
        # Obtener datos
        datos = obtener_datos_reporte(queryset, reporte.campos_json, reporte.configuracion_json)
        
        # Crear Excel
        output = io.BytesIO()
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos)
        
        if df.empty:
            return JsonResponse({
                'success': False,
                'message': 'No hay datos para exportar'
            })
        
        # Crear archivo Excel con formato
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reporte', index=False)
            
            # Formatear la hoja
            worksheet = writer.sheets['Reporte']
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Formatear encabezados
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
                cell.fill = cell.fill.copy(start_color="00B050", end_color="00B050")
        
        output.seek(0)
        
        # Crear respuesta
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        filename = f"{reporte.nombre}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Actualizar contador
        reporte.marcar_ejecutado()
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al exportar reporte: {str(e)}'
        })

@login_required
@admin_or_supervisor_required
def api_reportes_predefinidos(request):
    """API que devuelve reportes predefinidos del sistema"""
    try:
        tipo_reporte = request.GET.get('tipo', 'general')
        
        reportes = []
        
        if tipo_reporte == 'sla':
            # Reporte de SLA
            reportes.append({
                'nombre': 'Cumplimiento SLA por Etapa',
                'descripcion': 'Análisis del cumplimiento de SLA por etapa y pipeline',
                'tipo': 'sla',
                'datos': generar_reporte_sla()
            })
        
        elif tipo_reporte == 'productividad':
            # Reporte de productividad
            reportes.append({
                'nombre': 'Productividad por Usuario',
                'descripcion': 'Solicitudes procesadas por usuario en el período',
                'tipo': 'productividad',
                'datos': generar_reporte_productividad()
            })
        
        elif tipo_reporte == 'tiempos':
            # Reporte de tiempos
            reportes.append({
                'nombre': 'Tiempos Promedio por Etapa',
                'descripcion': 'Análisis de tiempos de procesamiento por etapa',
                'tipo': 'tiempos',
                'datos': generar_reporte_tiempos()
            })
        
        elif tipo_reporte == 'comite':
            # Reporte de comité
            reportes.append({
                'nombre': 'Participaciones en Comité',
                'descripcion': 'Análisis de participaciones y decisiones del comité',
                'tipo': 'comite',
                'datos': generar_reporte_comite()
            })
        
        else:
            # Reporte general
            reportes = [
                {
                    'nombre': 'Dashboard General',
                    'descripcion': 'Vista general del estado de las solicitudes',
                    'tipo': 'general',
                    'datos': generar_reporte_general()
                }
            ]
        
        return JsonResponse({
            'success': True,
            'reportes': reportes
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener reportes: {str(e)}'
        })

# ==========================================
# FUNCIONES AUXILIARES PARA REPORTES
# ==========================================

def aplicar_filtros_reporte(queryset, filtros):
    """Aplica filtros dinámicos a un queryset de solicitudes"""
    
    # Filtro por fechas
    if filtros.get('fecha_inicio'):
        try:
            fecha_inicio = datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_inicio)
        except:
            pass
    
    if filtros.get('fecha_fin'):
        try:
            fecha_fin = datetime.strptime(filtros['fecha_fin'], '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_fin)
        except:
            pass
    
    # Filtro por pipeline
    if filtros.get('pipeline_ids'):
        queryset = queryset.filter(pipeline_id__in=filtros['pipeline_ids'])
    
    # Filtro por etapa
    if filtros.get('etapa_ids'):
        queryset = queryset.filter(etapa_actual_id__in=filtros['etapa_ids'])
    
    # Filtro por usuario asignado
    if filtros.get('usuario_ids'):
        queryset = queryset.filter(asignada_a_id__in=filtros['usuario_ids'])
    
    # Filtro por estado SLA
    if filtros.get('estado_sla'):
        if filtros['estado_sla'] == 'vencido':
            # Filtrar solicitudes con SLA vencido
            queryset = queryset.filter(etapa_actual__isnull=False)
            # Nota: La lógica de SLA vencido se aplicaría en el procesamiento
        elif filtros['estado_sla'] == 'vigente':
            queryset = queryset.filter(etapa_actual__isnull=False)
    
    # Filtro por subestado
    if filtros.get('subestado_ids'):
        queryset = queryset.filter(subestado_actual_id__in=filtros['subestado_ids'])
    
    # Filtro por monto
    if filtros.get('monto_min'):
        try:
            monto_min = float(filtros['monto_min'])
            queryset = queryset.filter(cotizacion__auxMonto2__gte=monto_min)
        except:
            pass
    
    if filtros.get('monto_max'):
        try:
            monto_max = float(filtros['monto_max'])
            queryset = queryset.filter(cotizacion__auxMonto2__lte=monto_max)
        except:
            pass
    
    # Filtro por tipo de producto
    if filtros.get('tipo_producto'):
        queryset = queryset.filter(cotizacion__tipoPrestamo=filtros['tipo_producto'])
    
    return queryset

def obtener_datos_reporte(queryset, campos, configuracion):
    """Extrae los datos según los campos configurados"""
    datos = []
    
    for solicitud in queryset:
        fila = {}
        
        for campo in campos:
            if campo == 'codigo':
                fila['Código'] = solicitud.codigo
            elif campo == 'pipeline':
                fila['Pipeline'] = solicitud.pipeline.nombre if solicitud.pipeline else ''
            elif campo == 'etapa_actual':
                fila['Etapa Actual'] = solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Completada'
            elif campo == 'subestado':
                fila['Subestado'] = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ''
            elif campo == 'cliente_nombre':
                fila['Cliente'] = solicitud.cliente_nombre
            elif campo == 'cliente_cedula':
                fila['Cédula'] = solicitud.cliente_cedula
            elif campo == 'monto':
                fila['Monto'] = solicitud.monto_formateado
            elif campo == 'producto':
                fila['Producto'] = solicitud.producto_descripcion
            elif campo == 'creada_por':
                fila['Creado Por'] = solicitud.creada_por.get_full_name() if solicitud.creada_por else ''
            elif campo == 'asignada_a':
                fila['Asignado A'] = solicitud.asignada_a.get_full_name() if solicitud.asignada_a else ''
            elif campo == 'fecha_creacion':
                fila['Fecha Creación'] = solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            elif campo == 'fecha_actualizacion':
                fila['Última Actualización'] = solicitud.fecha_ultima_actualizacion.strftime('%d/%m/%Y %H:%M')
            elif campo == 'prioridad':
                fila['Prioridad'] = solicitud.prioridad or 'Media'
            elif campo == 'tiempo_en_etapa':
                if solicitud.etapa_actual:
                    tiempo = timezone.now() - solicitud.fecha_ultima_actualizacion
                    fila['Tiempo en Etapa'] = f"{tiempo.days}d {tiempo.seconds//3600}h"
                else:
                    fila['Tiempo en Etapa'] = 'N/A'
            elif campo == 'sla_status':
                if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                    tiempo_transcurrido = timezone.now() - solicitud.fecha_ultima_actualizacion
                    sla_vencido = tiempo_transcurrido > solicitud.etapa_actual.sla
                    fila['Estado SLA'] = 'Vencido' if sla_vencido else 'Vigente'
                else:
                    fila['Estado SLA'] = 'N/A'
        
        datos.append(fila)
    
    return datos

def generar_reporte_sla():
    """Genera datos para el reporte de SLA"""
    etapas_con_sla = Etapa.objects.filter(sla__isnull=False)
    datos = []
    
    for etapa in etapas_con_sla:
        solicitudes_etapa = Solicitud.objects.filter(etapa_actual=etapa)
        total = solicitudes_etapa.count()
        vencidas = 0
        
        for solicitud in solicitudes_etapa:
            tiempo_transcurrido = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_transcurrido > etapa.sla:
                vencidas += 1
        
        cumplimiento = ((total - vencidas) / total * 100) if total > 0 else 0
        
        datos.append({
            'etapa': etapa.nombre,
            'pipeline': etapa.pipeline.nombre,
            'sla_horas': etapa.sla_horas,
            'total_solicitudes': total,
            'vencidas': vencidas,
            'cumplimiento_pct': round(cumplimiento, 2)
        })
    
    return datos

def generar_reporte_productividad():
    """Genera datos para el reporte de productividad"""
    hace_30_dias = timezone.now() - timedelta(days=30)
    
    usuarios = User.objects.filter(is_active=True).annotate(
        solicitudes_creadas=Count(
            'solicitudes_creadas',
            filter=Q(solicitudes_creadas__fecha_creacion__gte=hace_30_dias)
        ),
        solicitudes_procesadas=Count(
            'historial_responsable',
            filter=Q(
                historial_responsable__fecha_inicio__gte=hace_30_dias,
                historial_responsable__fecha_fin__isnull=False
            )
        ),
        comentarios_realizados=Count(
            'solicitudcomentario',
            filter=Q(solicitudcomentario__fecha_creacion__gte=hace_30_dias)
        )
    ).filter(
        Q(solicitudes_creadas__gt=0) | 
        Q(solicitudes_procesadas__gt=0) | 
        Q(comentarios_realizados__gt=0)
    ).order_by('-solicitudes_procesadas')
    
    datos = []
    for usuario in usuarios:
        datos.append({
            'usuario': usuario.get_full_name() or usuario.username,
            'solicitudes_creadas': usuario.solicitudes_creadas,
            'solicitudes_procesadas': usuario.solicitudes_procesadas,
            'comentarios': usuario.comentarios_realizados,
            'total_actividad': usuario.solicitudes_creadas + usuario.solicitudes_procesadas + usuario.comentarios_realizados
        })
    
    return datos

def generar_reporte_tiempos():
    """Genera datos para el reporte de tiempos"""
    etapas = Etapa.objects.all()
    datos = []
    
    for etapa in etapas:
        historiales = HistorialSolicitud.objects.filter(
            etapa=etapa,
            fecha_fin__isnull=False
        )
        
        if historiales.exists():
            tiempos = []
            for historial in historiales:
                tiempo_horas = (historial.fecha_fin - historial.fecha_inicio).total_seconds() / 3600
                tiempos.append(tiempo_horas)
            
            datos.append({
                'etapa': etapa.nombre,
                'pipeline': etapa.pipeline.nombre,
                'sla_horas': etapa.sla_horas,
                'tiempo_promedio': round(sum(tiempos) / len(tiempos), 2),
                'tiempo_minimo': round(min(tiempos), 2),
                'tiempo_maximo': round(max(tiempos), 2),
                'total_procesadas': len(tiempos)
            })
    
    return datos

def generar_reporte_comite():
    """Genera datos para el reporte de comité"""
    participaciones = ParticipacionComite.objects.select_related(
        'solicitud', 'nivel', 'usuario'
    ).order_by('-fecha_creacion')[:100]
    
    datos = []
    for participacion in participaciones:
        datos.append({
            'solicitud': participacion.solicitud.codigo,
            'nivel': participacion.nivel.nombre,
            'usuario': participacion.usuario.get_full_name() if participacion.usuario else '',
            'resultado': participacion.get_resultado_display(),
            'fecha': participacion.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'comentario': participacion.comentario[:100] + '...' if len(participacion.comentario) > 100 else participacion.comentario
        })
    
    return datos

def generar_reporte_general():
    """Genera datos para el reporte general"""
    datos = {
        'resumen': {
            'total_solicitudes': Solicitud.objects.count(),
            'solicitudes_activas': Solicitud.objects.filter(etapa_actual__isnull=False).count(),
            'solicitudes_completadas': Solicitud.objects.filter(etapa_actual__isnull=True).count(),
        },
        'por_pipeline': list(Pipeline.objects.annotate(
            total=Count('solicitud'),
            activas=Count('solicitud', filter=Q(solicitud__etapa_actual__isnull=False))
        ).values('nombre', 'total', 'activas')),
        'usuarios_activos': User.objects.filter(
            solicitudes_asignadas__isnull=False
        ).distinct().count()
    }
    
    return datos
