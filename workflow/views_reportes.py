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
@require_http_methods(["POST"])
def api_crear_reporte(request):
    """API para crear un nuevo reporte personalizado"""
    try:
        # Log para debug
        print(f"Recibiendo datos para crear reporte: {request.body}")
        
        data = json.loads(request.body)
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return JsonResponse({
                'success': False,
                'message': 'El nombre del reporte es obligatorio'
            })
        
        if not data.get('campos') or len(data.get('campos', [])) == 0:
            return JsonResponse({
                'success': False,
                'message': 'Debe seleccionar al menos un campo'
            })
        
        # Crear el reporte
        reporte = ReportePersonalizado.objects.create(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', ''),
            usuario=request.user,
            filtros_json=data.get('filtros', {}),
            campos_json=data.get('campos', []),
            configuracion_json=data.get('configuracion', {}),
            es_publico=data.get('es_publico', False),
            es_favorito=data.get('es_favorito', False)
        )
        
        # Agregar grupos si es público
        if reporte.es_publico and data.get('grupos_compartidos'):
            grupos = Group.objects.filter(id__in=data.get('grupos_compartidos'))
            reporte.grupos_compartidos.set(grupos)
        
        print(f"Reporte creado exitosamente: {reporte.id}")
        
        return JsonResponse({
            'success': True,
            'reporte_id': reporte.id,
            'message': 'Reporte creado exitosamente'
        })
        
    except json.JSONDecodeError as e:
        print(f"Error decodificando JSON: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error en el formato de datos: {str(e)}'
        })
    except Exception as e:
        print(f"Error inesperado creando reporte: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al crear reporte: {str(e)}'
        })


@login_required
@admin_or_supervisor_required
def api_obtener_reportes_usuario(request):
    """API para obtener los reportes personalizados del usuario actual"""
    try:
        reportes_usuario = ReportePersonalizado.objects.filter(usuario=request.user).order_by('-fecha_modificacion')
        reportes_favoritos = ReportePersonalizado.objects.filter(
            usuario=request.user, es_favorito=True
        ).order_by('-fecha_modificacion')
        
        # Convertir a formato JSON
        reportes_data = []
        for reporte in reportes_usuario:
            reportes_data.append({
                'id': reporte.id,
                'nombre': reporte.nombre,
                'descripcion': reporte.descripcion or 'Sin descripción',
                'es_favorito': reporte.es_favorito,
                'es_publico': reporte.es_publico,
                'veces_ejecutado': reporte.veces_ejecutado,
                'fecha_modificacion': reporte.fecha_modificacion.strftime('%d/%m/%Y %H:%M'),
                'ultima_ejecucion': reporte.ultima_ejecucion.strftime('%d/%m/%Y %H:%M') if reporte.ultima_ejecucion else 'Nunca ejecutado'
            })
        
        favoritos_data = []
        for reporte in reportes_favoritos:
            favoritos_data.append({
                'id': reporte.id,
                'nombre': reporte.nombre,
                'descripcion': reporte.descripcion or 'Sin descripción',
                'veces_ejecutado': reporte.veces_ejecutado,
                'ultima_ejecucion': reporte.ultima_ejecucion.strftime('%d/%m/%Y %H:%M') if reporte.ultima_ejecucion else 'Nunca ejecutado'
            })
        
        return JsonResponse({
            'success': True,
            'reportes_usuario': reportes_data,
            'reportes_favoritos': favoritos_data,
            'total_reportes': len(reportes_data)
        })
        
    except Exception as e:
        print(f"Error obteniendo reportes del usuario: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener reportes: {str(e)}'
        })


@login_required
@admin_or_supervisor_required
def api_crear_reporte_prueba(request):
    """API para crear un reporte de prueba con datos básicos"""
    try:
        # Crear un reporte de prueba simple
        reporte = ReportePersonalizado.objects.create(
            nombre='Reporte de Prueba',
            descripcion='Reporte de prueba para verificar exportación',
            usuario=request.user,
            filtros_json={},  # Sin filtros para obtener todas las solicitudes
            campos_json=['codigo', 'pipeline', 'etapa_actual', 'cliente_nombre', 'fecha_creacion'],
            configuracion_json={},
            es_publico=False,
            es_favorito=False
        )
        
        print(f"Reporte de prueba creado: {reporte.id}")
        
        return JsonResponse({
            'success': True,
            'reporte_id': reporte.id,
            'message': 'Reporte de prueba creado exitosamente'
        })
        
    except Exception as e:
        print(f"Error creando reporte de prueba: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al crear reporte de prueba: {str(e)}'
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
        print(f"Exportando reporte ID: {reporte_id}")
        reporte = get_object_or_404(ReportePersonalizado, id=reporte_id)
        
        # Verificar permisos
        if not reporte.puede_ver(request.user):
            print(f"Usuario {request.user.username} no tiene permisos para exportar reporte {reporte_id}")
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para exportar este reporte'
            })
        
        # Obtener parámetros adicionales
        filtros_extra = {}
        if request.method == 'POST':
            try:
                filtros_extra = json.loads(request.body).get('filtros_extra', {})
            except json.JSONDecodeError:
                filtros_extra = {}
        
        print(f"Filtros del reporte: {reporte.filtros_json}")
        print(f"Filtros extra: {filtros_extra}")
        
        # Construir consulta
        queryset = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a', 'cliente', 'cotizacion'
        )
        
        filtros = {**reporte.filtros_json, **filtros_extra}
        queryset = aplicar_filtros_reporte(queryset, filtros)
        
        print(f"QuerySet count: {queryset.count()}")
        
        # Obtener datos
        datos = obtener_datos_reporte(queryset, reporte.campos_json, reporte.configuracion_json)
        
        print(f"Datos obtenidos: {len(datos)} registros")
        
        # Crear Excel
        output = io.BytesIO()
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos)
        
        if df.empty:
            print("DataFrame está vacío")
            return JsonResponse({
                'success': False,
                'message': 'No hay datos para exportar con los filtros aplicados'
            })
        
        print(f"DataFrame shape: {df.shape}")
        print(f"Columnas: {list(df.columns)}")
        
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
        file_size = len(output.getvalue())
        print(f"Archivo Excel generado: {file_size} bytes")
        
        # Crear respuesta
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        filename = f"{reporte.nombre}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Actualizar contador
        reporte.marcar_ejecutado()
        
        print(f"Reporte exportado exitosamente: {filename}")
        return response
        
    except Exception as e:
        print(f"Error exportando reporte {reporte_id}: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al exportar reporte: {str(e)}'
        })

@login_required
@admin_or_supervisor_required
@require_http_methods(["POST"])
def api_eliminar_reporte(request, reporte_id):
    """API para eliminar un reporte personalizado"""
    try:
        reporte = get_object_or_404(ReportePersonalizado, id=reporte_id)
        
        # Verificar permisos - solo el creador puede eliminar
        if reporte.usuario != request.user and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para eliminar este reporte'
            })
        
        # Eliminar el reporte
        nombre_reporte = reporte.nombre
        reporte.delete()
        
        print(f"Reporte eliminado: {nombre_reporte} por usuario {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Reporte "{nombre_reporte}" eliminado exitosamente'
        })
        
    except Exception as e:
        print(f"Error eliminando reporte {reporte_id}: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar reporte: {str(e)}'
        })

@login_required
@admin_or_supervisor_required
def api_reportes_predefinidos(request):
    """API que devuelve reportes predefinidos del sistema"""
    try:
        tipo_reporte = request.GET.get('tipo', 'general')
        exportar = request.GET.get('exportar', '0') == '1'
        
        print(f"API Reportes Predefinidos - Tipo: {tipo_reporte}, Exportar: {exportar}")
        
        reportes = []
        
        if tipo_reporte == 'dashboard_general':
            # 1. Dashboard General - Vista completa del estado
            datos = generar_dashboard_general()
            reportes.append({
                'nombre': 'Dashboard General',
                'descripcion': 'Vista completa del estado de todas las solicitudes',
                'tipo': 'dashboard_general',
                'datos': datos
            })
        
        elif tipo_reporte == 'sla_cumplimiento':
            # 2. Cumplimiento SLA por Etapa
            datos = generar_reporte_sla_cumplimiento()
            reportes.append({
                'nombre': 'Cumplimiento SLA por Etapa',
                'descripcion': 'Análisis detallado del cumplimiento de SLA por etapa y pipeline',
                'tipo': 'sla_cumplimiento',
                'datos': datos
            })
        
        elif tipo_reporte == 'productividad_usuarios':
            # 3. Productividad por Usuario
            datos = generar_reporte_productividad_usuarios()
            reportes.append({
                'nombre': 'Productividad por Usuario',
                'descripcion': 'Solicitudes procesadas por usuario en el período',
                'tipo': 'productividad_usuarios',
                'datos': datos
            })
        
        elif tipo_reporte == 'tiempos_etapas':
            # 4. Tiempos Promedio por Etapa
            datos = generar_reporte_tiempos_etapas()
            reportes.append({
                'nombre': 'Tiempos Promedio por Etapa',
                'descripcion': 'Análisis de tiempos de procesamiento por etapa',
                'tipo': 'tiempos_etapas',
                'datos': datos
            })
        
        elif tipo_reporte == 'comite_participaciones':
            # 5. Participaciones en Comité
            datos = generar_reporte_comite_participaciones()
            reportes.append({
                'nombre': 'Participaciones en Comité',
                'descripcion': 'Análisis de participaciones y decisiones del comité',
                'tipo': 'comite_participaciones',
                'datos': datos
            })
        
        elif tipo_reporte == 'clientes_productos':
            # 6. Análisis de Clientes y Productos
            datos = generar_reporte_clientes_productos()
            reportes.append({
                'nombre': 'Análisis de Clientes y Productos',
                'descripcion': 'Distribución de clientes por producto y monto',
                'tipo': 'clientes_productos',
                'datos': datos
            })
        
        elif tipo_reporte == 'requisitos_cumplimiento':
            # 7. Cumplimiento de Requisitos
            datos = generar_reporte_requisitos_cumplimiento()
            reportes.append({
                'nombre': 'Cumplimiento de Requisitos',
                'descripcion': 'Estado de cumplimiento de requisitos por solicitud',
                'tipo': 'requisitos_cumplimiento',
                'datos': datos
            })
        
        elif tipo_reporte == 'origen_solicitudes':
            # 8. Análisis por Origen de Solicitudes
            datos = generar_reporte_origen_solicitudes()
            reportes.append({
                'nombre': 'Análisis por Origen de Solicitudes',
                'descripcion': 'Distribución de solicitudes por canal de origen',
                'tipo': 'origen_solicitudes',
                'datos': datos
            })
        
        elif tipo_reporte == 'prioridades_urgentes':
            # 9. Solicitudes de Alta Prioridad
            datos = generar_reporte_prioridades_urgentes()
            reportes.append({
                'nombre': 'Solicitudes de Alta Prioridad',
                'descripcion': 'Solicitudes urgentes que requieren atención inmediata',
                'tipo': 'prioridades_urgentes',
                'datos': datos
            })
        
        elif tipo_reporte == 'calificaciones_compliance':
            # 10. Calificaciones de Compliance
            datos = generar_reporte_calificaciones_compliance()
            reportes.append({
                'nombre': 'Calificaciones de Compliance',
                'descripcion': 'Estado de calificaciones de campos de compliance',
                'tipo': 'calificaciones_compliance',
                'datos': datos
            })
        
        else:
            # Reporte general por defecto
            datos = generar_dashboard_general()
            reportes = [
                {
                    'nombre': 'Dashboard General',
                    'descripcion': 'Vista general del estado de las solicitudes',
                    'tipo': 'general',
                    'datos': datos
                }
            ]
        
        # Si se solicita exportación, devolver Excel
        if exportar and reportes:
            reporte = reportes[0]  # Tomar el primer reporte
            datos = reporte['datos']
            
            if not datos:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay datos para exportar'
                })
            
            # Crear DataFrame y exportar a Excel
            df = pd.DataFrame(datos)
            
            # Crear respuesta con archivo Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Reporte', index=False)
            
            output.seek(0)
            
            # Crear respuesta HTTP con archivo
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}.xlsx"'
            return response
        
        # Devolver JSON normal
        print(f"API Reportes Predefinidos - Devolviendo {len(reportes)} reportes")
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
            # ==========================================
            # CAMPOS BÁSICOS DE SOLICITUD
            # ==========================================
            if campo == 'codigo':
                fila['Código'] = solicitud.codigo
            elif campo == 'pipeline':
                fila['Pipeline'] = solicitud.pipeline.nombre if solicitud.pipeline else ''
            elif campo == 'etapa_actual':
                fila['Etapa Actual'] = solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Completada'
            elif campo == 'subestado_actual':
                fila['Subestado Actual'] = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ''
            elif campo == 'creada_por':
                fila['Creado Por'] = solicitud.creada_por.get_full_name() if solicitud.creada_por else ''
            elif campo == 'asignada_a':
                fila['Asignado A'] = solicitud.asignada_a.get_full_name() if solicitud.asignada_a else ''
            elif campo == 'propietario':
                fila['Propietario'] = solicitud.propietario.get_full_name() if solicitud.propietario else ''
            elif campo == 'fecha_creacion':
                fila['Fecha Creación'] = solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            elif campo == 'fecha_ultima_actualizacion':
                fila['Última Actualización'] = solicitud.fecha_ultima_actualizacion.strftime('%d/%m/%Y %H:%M')
            elif campo == 'prioridad':
                fila['Prioridad'] = solicitud.prioridad or 'Media'
            elif campo == 'etiquetas_oficial':
                fila['Etiquetas Oficial'] = solicitud.etiquetas_oficial or ''
            elif campo == 'origen':
                fila['Origen'] = solicitud.origen or ''
            elif campo == 'motivo_consulta':
                fila['Motivo Consulta'] = solicitud.motivo_consulta or ''
            elif campo == 'observaciones':
                fila['Observaciones'] = solicitud.observaciones or ''
            
            # ==========================================
            # CAMPOS DE CLIENTE (CANAL DIGITAL)
            # ==========================================
            elif campo == 'cliente_nombre':
                fila['Cliente'] = solicitud.cliente_nombre or (solicitud.cliente.nombreCliente if solicitud.cliente else '')
            elif campo == 'cliente_cedula':
                fila['Cédula'] = solicitud.cliente_cedula or (solicitud.cliente.cedulaCliente if solicitud.cliente else '')
            elif campo == 'cliente_telefono':
                fila['Teléfono'] = solicitud.cliente_telefono or ''
            elif campo == 'cliente_email':
                fila['Email'] = solicitud.cliente_email or ''
            elif campo == 'producto_solicitado':
                fila['Producto Solicitado'] = solicitud.producto_solicitado or ''
            elif campo == 'monto_solicitado':
                fila['Monto Solicitado'] = solicitud.monto_formateado
            
            # ==========================================
            # CAMPOS DE CLIENTE (MODELO PACIFICO)
            # ==========================================
            elif campo == 'cliente_fecha_nacimiento':
                if solicitud.cliente:
                    fila['Fecha Nacimiento'] = solicitud.cliente.fechaNacimiento.strftime('%d/%m/%Y') if solicitud.cliente.fechaNacimiento else ''
                else:
                    fila['Fecha Nacimiento'] = ''
            elif campo == 'cliente_edad':
                fila['Edad'] = solicitud.cliente.edad if solicitud.cliente else ''
            elif campo == 'cliente_sexo':
                fila['Sexo'] = solicitud.cliente.sexo if solicitud.cliente else ''
            elif campo == 'cliente_jubilado':
                fila['Jubilado'] = solicitud.cliente.jubilado if solicitud.cliente else ''
            
            # ==========================================
            # CAMPOS DE COTIZACIÓN
            # ==========================================
            elif campo == 'cotizacion_oficial':
                fila['Oficial'] = solicitud.cotizacion.oficial if solicitud.cotizacion else ''
            elif campo == 'cotizacion_sucursal':
                fila['Sucursal'] = solicitud.cotizacion.sucursal if solicitud.cotizacion else ''
            elif campo == 'cotizacion_tipo_prestamo':
                fila['Tipo Préstamo'] = solicitud.cotizacion.tipoPrestamo if solicitud.cotizacion else ''
            elif campo == 'cotizacion_monto_prestamo':
                fila['Monto Préstamo'] = f"${solicitud.cotizacion.montoPrestamo:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.montoPrestamo else ''
            elif campo == 'cotizacion_plazo_pago':
                fila['Plazo Pago'] = solicitud.cotizacion.plazoPago if solicitud.cotizacion else ''
            elif campo == 'cotizacion_tasa_interes':
                fila['Tasa Interés'] = f"{solicitud.cotizacion.tasaInteres}%" if solicitud.cotizacion and solicitud.cotizacion.tasaInteres else ''
            elif campo == 'cotizacion_sector':
                fila['Sector'] = solicitud.cotizacion.sector if solicitud.cotizacion else ''
            elif campo == 'cotizacion_patrono':
                fila['Patrono'] = solicitud.cotizacion.patrono if solicitud.cotizacion else ''
            elif campo == 'cotizacion_vendedor':
                fila['Vendedor'] = solicitud.cotizacion.vendedor if solicitud.cotizacion else ''
            elif campo == 'cotizacion_vendedor_tipo':
                fila['Tipo Vendedor'] = solicitud.cotizacion.vendedorTipo if solicitud.cotizacion else ''
            elif campo == 'cotizacion_apc_score':
                fila['APC Score'] = solicitud.cotizacion.apcScore if solicitud.cotizacion else ''
            elif campo == 'cotizacion_apc_pi':
                fila['APC PI'] = f"${solicitud.cotizacion.apcPI:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.apcPI else ''
            
            # ==========================================
            # CAMPOS DE HISTORIAL
            # ==========================================
            elif campo == 'historial_etapas':
                historial = solicitud.historial.all().order_by('fecha_inicio')
                etapas = [h.etapa.nombre for h in historial]
                fila['Historial Etapas'] = ' → '.join(etapas) if etapas else ''
            elif campo == 'tiempo_total_proceso':
                if solicitud.historial.exists():
                    primer_registro = solicitud.historial.earliest('fecha_inicio')
                    tiempo_total = timezone.now() - primer_registro.fecha_inicio
                    fila['Tiempo Total Proceso'] = f"{tiempo_total.days}d {tiempo_total.seconds//3600}h"
                else:
                    fila['Tiempo Total Proceso'] = 'N/A'
            elif campo == 'etapas_completadas':
                historial_completado = solicitud.historial.filter(fecha_fin__isnull=False).count()
                fila['Etapas Completadas'] = historial_completado
            
            # ==========================================
            # CAMPOS DE TIEMPO Y SLA
            # ==========================================
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
            elif campo == 'sla_vencido':
                if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                    tiempo_transcurrido = timezone.now() - solicitud.fecha_ultima_actualizacion
                    fila['SLA Vencido'] = 'Sí' if tiempo_transcurrido > solicitud.etapa_actual.sla else 'No'
                else:
                    fila['SLA Vencido'] = 'N/A'
            
            # ==========================================
            # CAMPOS DE REQUISITOS
            # ==========================================
            elif campo == 'requisitos_total':
                fila['Total Requisitos'] = solicitud.requisitos.count()
            elif campo == 'requisitos_cumplidos':
                fila['Requisitos Cumplidos'] = solicitud.requisitos.filter(cumplido=True).count()
            elif campo == 'requisitos_pendientes':
                fila['Requisitos Pendientes'] = solicitud.requisitos.filter(cumplido=False).count()
            elif campo == 'porcentaje_cumplimiento_requisitos':
                total = solicitud.requisitos.count()
                if total > 0:
                    cumplidos = solicitud.requisitos.filter(cumplido=True).count()
                    porcentaje = (cumplidos / total) * 100
                    fila['% Cumplimiento Requisitos'] = f"{porcentaje:.1f}%"
                else:
                    fila['% Cumplimiento Requisitos'] = 'N/A'
            
            # ==========================================
            # CAMPOS DE COMENTARIOS
            # ==========================================
            elif campo == 'comentarios_total':
                fila['Total Comentarios'] = solicitud.comentarios.count()
            elif campo == 'comentarios_general':
                comentarios_general = solicitud.comentarios.filter(tipo='general').count()
                fila['Comentarios Generales'] = comentarios_general
            elif campo == 'comentarios_analista':
                comentarios_analista = solicitud.comentarios.filter(tipo='analista').count()
                fila['Comentarios Analista'] = comentarios_analista
            elif campo == 'ultimo_comentario':
                ultimo = solicitud.comentarios.order_by('-fecha_creacion').first()
                fila['Último Comentario'] = ultimo.comentario[:100] + '...' if ultimo else ''
            
            # ==========================================
            # CAMPOS DE CALIFICACIONES COMPLIANCE
            # ==========================================
            elif campo == 'calificaciones_total':
                fila['Total Calificaciones'] = solicitud.calificaciones_campos.count()
            elif campo == 'calificaciones_buenas':
                fila['Calificaciones Buenas'] = solicitud.calificaciones_campos.filter(estado='bueno').count()
            elif campo == 'calificaciones_malas':
                fila['Calificaciones Malas'] = solicitud.calificaciones_campos.filter(estado='malo').count()
            elif campo == 'calificaciones_sin_calificar':
                fila['Sin Calificar'] = solicitud.calificaciones_campos.filter(estado='sin_calificar').count()
            
            # ==========================================
            # CAMPOS DE COMITÉ
            # ==========================================
            elif campo == 'comite_participaciones':
                fila['Participaciones Comité'] = solicitud.participaciones_comite.count()
            elif campo == 'comite_escalamientos':
                fila['Escalamientos Comité'] = solicitud.escalamientos_comite.count()
            elif campo == 'comite_ultima_participacion':
                ultima = solicitud.participaciones_comite.order_by('-fecha_creacion').first()
                fila['Última Participación Comité'] = ultima.fecha_creacion.strftime('%d/%m/%Y %H:%M') if ultima else ''
            
            # ==========================================
            # CAMPOS DE CAMPOS PERSONALIZADOS
            # ==========================================
            elif campo == 'campos_personalizados':
                fila['Campos Personalizados'] = solicitud.valores_personalizados.count()
            
            # ==========================================
            # CAMPOS DE DEBIDA DILIGENCIA
            # ==========================================
            elif campo == 'debida_diligencia_estado':
                if solicitud.cliente and hasattr(solicitud.cliente, 'debida_diligencia'):
                    fila['Estado Debida Diligencia'] = solicitud.cliente.debida_diligencia.get_estado_display()
                else:
                    fila['Estado Debida Diligencia'] = 'N/A'
            
            # ==========================================
            # CAMPOS DE DOCUMENTOS COTIZACIÓN
            # ==========================================
            elif campo == 'documentos_cotizacion':
                if solicitud.cotizacion:
                    fila['Documentos Cotización'] = solicitud.cotizacion.cotizaciondocumento_set.count()
                else:
                    fila['Documentos Cotización'] = 0
            
            # ==========================================
            # CAMPOS DE CÁLCULOS FINANCIEROS
            # ==========================================
            elif campo == 'monto':
                fila['Monto'] = solicitud.monto_formateado
            elif campo == 'producto':
                fila['Producto'] = solicitud.producto_descripcion
            elif campo == 'tasa_estimada':
                fila['Tasa Estimada'] = f"{solicitud.cotizacion.tasaEstimada}%" if solicitud.cotizacion and solicitud.cotizacion.tasaEstimada else ''
            elif campo == 'tasa_bruta':
                fila['Tasa Bruta'] = f"{solicitud.cotizacion.tasaBruta}%" if solicitud.cotizacion and solicitud.cotizacion.tasaBruta else ''
            elif campo == 'comision_cierre':
                fila['Comisión Cierre'] = f"${solicitud.cotizacion.comiCierre:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.comiCierre else ''
            
            # ==========================================
            # CAMPOS DE INFORMACIÓN DEL AUTO (si aplica)
            # ==========================================
            elif campo == 'auto_marca':
                fila['Marca Auto'] = solicitud.cotizacion.marca if solicitud.cotizacion else ''
            elif campo == 'auto_modelo':
                fila['Modelo Auto'] = solicitud.cotizacion.modelo if solicitud.cotizacion else ''
            elif campo == 'auto_year':
                fila['Año Auto'] = solicitud.cotizacion.yearCarro if solicitud.cotizacion else ''
            elif campo == 'auto_valor':
                fila['Valor Auto'] = f"${solicitud.cotizacion.valorAuto:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.valorAuto else ''
            elif campo == 'auto_cashback':
                fila['Cashback'] = f"${solicitud.cotizacion.cashback:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.cashback else ''
            elif campo == 'auto_abono':
                fila['Abono'] = f"${solicitud.cotizacion.abono:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.abono else ''
            
            # ==========================================
            # CAMPOS DE INFORMACIÓN LABORAL
            # ==========================================
            elif campo == 'tiempo_servicio':
                fila['Tiempo Servicio'] = solicitud.cotizacion.tiempoServicio if solicitud.cotizacion else ''
            elif campo == 'ingresos':
                fila['Ingresos'] = f"${solicitud.cotizacion.ingresos:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.ingresos else ''
            elif campo == 'nombre_empresa':
                fila['Nombre Empresa'] = solicitud.cotizacion.nombreEmpresa if solicitud.cotizacion else ''
            elif campo == 'posicion':
                fila['Posición'] = solicitud.cotizacion.posicion if solicitud.cotizacion else ''
            elif campo == 'salario_base':
                fila['Salario Base'] = f"${solicitud.cotizacion.salarioBaseMensual:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.salarioBaseMensual else ''
            elif campo == 'salario_neto':
                fila['Salario Neto'] = f"${solicitud.cotizacion.salarioNeto:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.salarioNeto else ''
            
            # ==========================================
            # CAMPOS DE CODEUDOR
            # ==========================================
            elif campo == 'aplica_codeudor':
                fila['Aplica Codeudor'] = solicitud.cotizacion.aplicaCodeudor.title() if solicitud.cotizacion else ''
            elif campo == 'codeudor_nombre':
                fila['Codeudor Nombre'] = solicitud.cotizacion.codeudorNombre if solicitud.cotizacion else ''
            elif campo == 'codeudor_cedula':
                fila['Codeudor Cédula'] = solicitud.cotizacion.codeudorCedula if solicitud.cotizacion else ''
            elif campo == 'codeudor_ingresos':
                fila['Codeudor Ingresos'] = f"${solicitud.cotizacion.codeudorIngresos:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.codeudorIngresos else ''
            
            # ==========================================
            # CAMPOS DE SEGURO
            # ==========================================
            elif campo == 'financia_seguro':
                fila['Financia Seguro'] = 'Sí' if solicitud.cotizacion and solicitud.cotizacion.financiaSeguro else 'No'
            elif campo == 'monto_anual_seguro':
                fila['Monto Anual Seguro'] = f"${solicitud.cotizacion.montoanualSeguro:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.montoanualSeguro else ''
            elif campo == 'monto_mensual_seguro':
                fila['Monto Mensual Seguro'] = f"${solicitud.cotizacion.montoMensualSeguro:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.montoMensualSeguro else ''
            
            # ==========================================
            # CAMPOS DE FECHAS IMPORTANTES
            # ==========================================
            elif campo == 'fecha_inicio_pago':
                fila['Fecha Inicio Pago'] = solicitud.cotizacion.fechaInicioPago.strftime('%d/%m/%Y') if solicitud.cotizacion and solicitud.cotizacion.fechaInicioPago else ''
            elif campo == 'fecha_vencimiento':
                fila['Fecha Vencimiento'] = solicitud.cotizacion.fechaVencimiento.strftime('%d/%m/%Y') if solicitud.cotizacion and solicitud.cotizacion.fechaVencimiento else ''
            
            # ==========================================
            # CAMPOS DE RESULTADOS FINANCIEROS
            # ==========================================
            elif campo == 'tabla_total_pagos':
                fila['Total Pagos'] = f"${solicitud.cotizacion.tablaTotalPagos:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.tablaTotalPagos else ''
            elif campo == 'tabla_total_seguro':
                fila['Total Seguro'] = f"${solicitud.cotizacion.tablaTotalSeguro:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.tablaTotalSeguro else ''
            elif campo == 'tabla_total_interes':
                fila['Total Interés'] = f"${solicitud.cotizacion.tablaTotalInteres:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.tablaTotalInteres else ''
            elif campo == 'tabla_total_capital':
                fila['Total Capital'] = f"${solicitud.cotizacion.tablaTotalMontoCapital:,.2f}" if solicitud.cotizacion and solicitud.cotizacion.tablaTotalMontoCapital else ''
        
        datos.append(fila)
    
    return datos

# ==========================================
# FUNCIONES DE GENERACIÓN DE REPORTES
# ==========================================

def generar_dashboard_general():
    """1. Dashboard General - Vista completa del estado"""
    try:
        solicitudes = Solicitud.objects.select_related(
            'pipeline', 'etapa_actual', 'asignada_a', 'cliente'
        ).all()
        
        datos = []
        for solicitud in solicitudes:
            # Calcular tiempo en etapa actual
            tiempo_etapa = None
            if solicitud.etapa_actual:
                historial_actual = solicitud.historial.filter(
                    etapa=solicitud.etapa_actual
                ).order_by('-fecha_inicio').first()
                if historial_actual:
                    tiempo_etapa = (timezone.now() - historial_actual.fecha_inicio).total_seconds() / 3600
            
            # Estado SLA
            estado_sla = "Vigente"
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                if tiempo_etapa and tiempo_etapa > solicitud.etapa_actual.sla.total_seconds() / 3600:
                    estado_sla = "Vencido"
            
            datos.append({
                'Código': solicitud.codigo,
                'Pipeline': solicitud.pipeline.nombre if solicitud.pipeline else 'N/A',
                'Etapa Actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'N/A',
                'Cliente': solicitud.cliente_nombre or (solicitud.cliente.nombreCliente if solicitud.cliente else 'N/A'),
                'Cédula': solicitud.cliente_cedula or (solicitud.cliente.cedulaCliente if solicitud.cliente else 'N/A'),
                'Producto': solicitud.producto_solicitado or 'N/A',
                'Monto': float(solicitud.monto_solicitado) if solicitud.monto_solicitado else 0,
                'Asignado A': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else 'Sin asignar',
                'Prioridad': solicitud.prioridad or 'Sin definir',
                'Estado SLA': estado_sla,
                'Tiempo en Etapa (h)': round(tiempo_etapa, 2) if tiempo_etapa else 0,
                'Fecha Creación': solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'Origen': solicitud.origen or 'N/A'
            })
        
        return datos
    except Exception as e:
        print(f"Error en dashboard general: {e}")
        return []

def generar_reporte_sla_cumplimiento():
    """2. Cumplimiento SLA por Etapa"""
    try:
        etapas = Etapa.objects.select_related('pipeline').all()
        datos = []
        
        for etapa in etapas:
            solicitudes_etapa = Solicitud.objects.filter(etapa_actual=etapa)
            total_solicitudes = solicitudes_etapa.count()
            
            if total_solicitudes == 0:
                continue
            
            # Calcular cumplimiento SLA
            cumplimiento_sla = 0
            solicitudes_vencidas = 0
            
            for solicitud in solicitudes_etapa:
                historial_actual = solicitud.historial.filter(etapa=etapa).order_by('-fecha_inicio').first()
                if historial_actual and etapa.sla:
                    tiempo_etapa = (timezone.now() - historial_actual.fecha_inicio).total_seconds() / 3600
                    if tiempo_etapa > etapa.sla.total_seconds() / 3600:
                        solicitudes_vencidas += 1
            
            cumplimiento_sla = ((total_solicitudes - solicitudes_vencidas) / total_solicitudes) * 100
            
            datos.append({
                'Pipeline': etapa.pipeline.nombre,
                'Etapa': etapa.nombre,
                'SLA (horas)': etapa.sla_horas if etapa.sla else 'Sin SLA',
                'Total Solicitudes': total_solicitudes,
                'Solicitudes Vencidas': solicitudes_vencidas,
                'Cumplimiento SLA (%)': round(cumplimiento_sla, 2),
                'Tiempo Promedio (h)': round(etapa.sla.total_seconds() / 3600, 2) if etapa.sla else 0
            })
        
        return datos
    except Exception as e:
        print(f"Error en SLA cumplimiento: {e}")
        return []

def generar_reporte_productividad_usuarios():
    """3. Productividad por Usuario"""
    try:
        usuarios = User.objects.filter(is_active=True)
        datos = []
        
        for usuario in usuarios:
            # Solicitudes asignadas actualmente
            solicitudes_actuales = Solicitud.objects.filter(asignada_a=usuario).count()
            
            # Solicitudes procesadas en los últimos 30 días
            hace_30_dias = timezone.now() - timedelta(days=30)
            solicitudes_procesadas = HistorialSolicitud.objects.filter(
                usuario_responsable=usuario,
                fecha_inicio__gte=hace_30_dias
            ).count()
            
            # Solicitudes creadas
            solicitudes_creadas = Solicitud.objects.filter(
                creada_por=usuario,
                fecha_creacion__gte=hace_30_dias
            ).count()
            
            datos.append({
                'Usuario': usuario.get_full_name() or usuario.username,
                'Email': usuario.email,
                'Solicitudes Asignadas': solicitudes_actuales,
                'Solicitudes Procesadas (30 días)': solicitudes_procesadas,
                'Solicitudes Creadas (30 días)': solicitudes_creadas,
                'Total Actividad (30 días)': solicitudes_procesadas + solicitudes_creadas,
                'Último Acceso': usuario.last_login.strftime('%d/%m/%Y %H:%M') if usuario.last_login else 'Nunca'
            })
        
        return datos
    except Exception as e:
        print(f"Error en productividad usuarios: {e}")
        return []

def generar_reporte_tiempos_etapas():
    """4. Tiempos Promedio por Etapa"""
    try:
        etapas = Etapa.objects.select_related('pipeline').all()
        datos = []
        
        for etapa in etapas:
            historiales = HistorialSolicitud.objects.filter(etapa=etapa)
            total_historiales = historiales.count()
            
            if total_historiales == 0:
                continue
            
            # Calcular tiempos promedio
            tiempos = []
            for historial in historiales:
                if historial.fecha_fin:
                    tiempo = (historial.fecha_fin - historial.fecha_inicio).total_seconds() / 3600
                    tiempos.append(tiempo)
            
            tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
            tiempo_minimo = min(tiempos) if tiempos else 0
            tiempo_maximo = max(tiempos) if tiempos else 0
            
            datos.append({
                'Pipeline': etapa.pipeline.nombre,
                'Etapa': etapa.nombre,
                'SLA (horas)': etapa.sla_horas if etapa.sla else 'Sin SLA',
                'Total Solicitudes Procesadas': total_historiales,
                'Tiempo Promedio (h)': round(tiempo_promedio, 2),
                'Tiempo Mínimo (h)': round(tiempo_minimo, 2),
                'Tiempo Máximo (h)': round(tiempo_maximo, 2),
                'Cumplimiento SLA (%)': round((len([t for t in tiempos if t <= etapa.sla.total_seconds() / 3600]) / len(tiempos)) * 100, 2) if etapa.sla and tiempos else 0
            })
        
        return datos
    except Exception as e:
        print(f"Error en tiempos etapas: {e}")
        return []

def generar_reporte_comite_participaciones():
    """5. Participaciones en Comité"""
    try:
        participaciones = ParticipacionComite.objects.select_related(
            'solicitud', 'nivel', 'usuario'
        ).all()
        
        datos = []
        for participacion in participaciones:
            try:
                # Validar que la solicitud existe
                if not participacion.solicitud:
                    continue
                
                # Validar que el nivel existe
                if not participacion.nivel:
                    continue
                
                # Manejar comentario que puede ser None
                comentario = participacion.comentario or ''
                comentario_formateado = comentario[:100] + '...' if len(comentario) > 100 else comentario
                
                # Obtener nombre del usuario de forma segura
                nombre_usuario = 'N/A'
                if participacion.usuario:
                    try:
                        nombre_usuario = participacion.usuario.get_full_name() or participacion.usuario.username
                    except:
                        nombre_usuario = participacion.usuario.username if participacion.usuario.username else 'N/A'
                
                # Obtener resultado de forma segura
                resultado = 'N/A'
                try:
                    resultado = participacion.get_resultado_display()
                except:
                    resultado = participacion.resultado if participacion.resultado else 'N/A'
                
                datos.append({
                    'Código Solicitud': participacion.solicitud.codigo,
                    'Nivel Comité': participacion.nivel.nombre,
                    'Usuario': nombre_usuario,
                    'Resultado': resultado,
                    'Comentario': comentario_formateado,
                    'Fecha Participación': participacion.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                    'Pipeline': participacion.solicitud.pipeline.nombre if participacion.solicitud.pipeline else 'N/A',
                    'Etapa Actual': participacion.solicitud.etapa_actual.nombre if participacion.solicitud.etapa_actual else 'N/A'
                })
            except Exception as e:
                print(f"Error procesando participación {participacion.id}: {e}")
                continue
        
        return datos
    except Exception as e:
        print(f"Error en comité participaciones: {e}")
        return []

def generar_reporte_clientes_productos():
    """6. Análisis de Clientes y Productos"""
    try:
        solicitudes = Solicitud.objects.exclude(
            producto_solicitado__isnull=True
        ).exclude(
            producto_solicitado=''
        ).select_related('cliente')
        
        datos = []
        for solicitud in solicitudes:
            datos.append({
                'Código': solicitud.codigo,
                'Cliente': solicitud.cliente_nombre or (solicitud.cliente.nombreCliente if solicitud.cliente else 'N/A'),
                'Cédula': solicitud.cliente_cedula or (solicitud.cliente.cedulaCliente if solicitud.cliente else 'N/A'),
                'Teléfono': solicitud.cliente_telefono or 'N/A',
                'Email': solicitud.cliente_email or 'N/A',
                'Producto': solicitud.producto_solicitado,
                'Monto Solicitado': float(solicitud.monto_solicitado) if solicitud.monto_solicitado else 0,
                'Pipeline': solicitud.pipeline.nombre if solicitud.pipeline else 'N/A',
                'Etapa Actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'N/A',
                'Fecha Creación': solicitud.fecha_creacion.strftime('%d/%m/%Y'),
                'Origen': solicitud.origen or 'N/A'
            })
        
        return datos
    except Exception as e:
        print(f"Error en clientes productos: {e}")
        return []

def generar_reporte_requisitos_cumplimiento():
    """7. Cumplimiento de Requisitos"""
    try:
        requisitos_solicitud = RequisitoSolicitud.objects.select_related(
            'solicitud', 'requisito'
        ).all()
        
        datos = []
        for req_sol in requisitos_solicitud:
            datos.append({
                'Código Solicitud': req_sol.solicitud.codigo,
                'Pipeline': req_sol.solicitud.pipeline.nombre if req_sol.solicitud.pipeline else 'N/A',
                'Etapa Actual': req_sol.solicitud.etapa_actual.nombre if req_sol.solicitud.etapa_actual else 'N/A',
                'Requisito': req_sol.requisito.nombre,
                'Descripción': req_sol.requisito.descripcion,
                'Cumplido': 'Sí' if req_sol.cumplido else 'No',
                'Observaciones': req_sol.observaciones or 'Sin observaciones',
                'Fecha Creación Solicitud': req_sol.solicitud.fecha_creacion.strftime('%d/%m/%Y'),
                'Cliente': req_sol.solicitud.cliente_nombre or (req_sol.solicitud.cliente.nombreCliente if req_sol.solicitud.cliente else 'N/A')
            })
        
        return datos
    except Exception as e:
        print(f"Error en requisitos cumplimiento: {e}")
        return []

def generar_reporte_origen_solicitudes():
    """8. Análisis por Origen de Solicitudes"""
    try:
        solicitudes = Solicitud.objects.all()
        
        # Agrupar por origen
        origenes = {}
        for solicitud in solicitudes:
            origen = solicitud.origen or 'Sin origen'
            if origen not in origenes:
                origenes[origen] = {
                    'total': 0,
                    'activas': 0,
                    'completadas': 0,
                    'monto_total': 0,
                    'productos': {}
                }
            
            origenes[origen]['total'] += 1
            
            if solicitud.etapa_actual:
                origenes[origen]['activas'] += 1
            else:
                origenes[origen]['completadas'] += 1
            
            if solicitud.monto_solicitado:
                origenes[origen]['monto_total'] += float(solicitud.monto_solicitado)
            
            producto = solicitud.producto_solicitado or 'Sin producto'
            if producto not in origenes[origen]['productos']:
                origenes[origen]['productos'][producto] = 0
            origenes[origen]['productos'][producto] += 1
        
        datos = []
        for origen, stats in origenes.items():
            datos.append({
                'Origen': origen,
                'Total Solicitudes': stats['total'],
                'Solicitudes Activas': stats['activas'],
                'Solicitudes Completadas': stats['completadas'],
                'Monto Total': round(stats['monto_total'], 2),
                'Producto Principal': max(stats['productos'].items(), key=lambda x: x[1])[0] if stats['productos'] else 'N/A',
                'Distribución Productos': ', '.join([f"{prod}: {cant}" for prod, cant in stats['productos'].items()])
            })
        
        return datos
    except Exception as e:
        print(f"Error en origen solicitudes: {e}")
        return []

def generar_reporte_prioridades_urgentes():
    """9. Solicitudes de Alta Prioridad"""
    try:
        solicitudes_urgentes = Solicitud.objects.filter(
            prioridad='Alta'
        ).select_related('pipeline', 'etapa_actual', 'asignada_a', 'cliente')
        
        datos = []
        for solicitud in solicitudes_urgentes:
            # Calcular tiempo en etapa actual
            tiempo_etapa = None
            if solicitud.etapa_actual:
                historial_actual = solicitud.historial.filter(
                    etapa=solicitud.etapa_actual
                ).order_by('-fecha_inicio').first()
                if historial_actual:
                    tiempo_etapa = (timezone.now() - historial_actual.fecha_inicio).total_seconds() / 3600
            
            # Estado SLA
            estado_sla = "Vigente"
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                if tiempo_etapa and tiempo_etapa > solicitud.etapa_actual.sla.total_seconds() / 3600:
                    estado_sla = "Vencido"
            
            datos.append({
                'Código': solicitud.codigo,
                'Cliente': solicitud.cliente_nombre or solicitud.cliente.nombreCliente if solicitud.cliente else 'N/A',
                'Cédula': solicitud.cliente_cedula or solicitud.cliente.cedulaCliente if solicitud.cliente else 'N/A',
                'Producto': solicitud.producto_solicitado or 'N/A',
                'Monto': float(solicitud.monto_solicitado) if solicitud.monto_solicitado else 0,
                'Pipeline': solicitud.pipeline.nombre if solicitud.pipeline else 'N/A',
                'Etapa Actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'N/A',
                'Asignado A': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else 'Sin asignar',
                'Estado SLA': estado_sla,
                'Tiempo en Etapa (h)': round(tiempo_etapa, 2) if tiempo_etapa else 0,
                'Fecha Creación': solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'Origen': solicitud.origen or 'N/A',
                'Observaciones': solicitud.observaciones or 'Sin observaciones'
            })
        
        return datos
    except Exception as e:
        print(f"Error en prioridades urgentes: {e}")
        return []

def generar_reporte_calificaciones_compliance():
    """10. Calificaciones de Compliance"""
    try:
        calificaciones = CalificacionCampo.objects.select_related(
            'solicitud', 'usuario'
        ).all()
        
        datos = []
        for calificacion in calificaciones:
            datos.append({
                'Código Solicitud': calificacion.solicitud.codigo,
                'Campo': calificacion.campo,
                'Estado': calificacion.get_estado_display(),
                'Comentario': calificacion.comentario or 'Sin comentarios',
                'Usuario Calificador': calificacion.usuario.get_full_name() or calificacion.usuario.username,
                'Fecha Calificación': calificacion.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'Pipeline': calificacion.solicitud.pipeline.nombre if calificacion.solicitud.pipeline else 'N/A',
                'Etapa Actual': calificacion.solicitud.etapa_actual.nombre if calificacion.solicitud.etapa_actual else 'N/A',
                'Cliente': calificacion.solicitud.cliente_nombre or calificacion.solicitud.cliente.nombreCliente if calificacion.solicitud.cliente else 'N/A'
            })
        
        return datos
    except Exception as e:
        print(f"Error en calificaciones compliance: {e}")
        return []
