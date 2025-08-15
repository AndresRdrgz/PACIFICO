from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
import logging
import json
import json
import logging

from .modelsWorkflow import (
    Solicitud, HistorialSolicitud, Etapa, SubEstado, 
    SolicitudComentario, ReconsideracionSolicitud
)
from pacifico.models import Cotizacion
from pacifico.models import Cotizacion
from .views_workflow import notify_solicitud_change

logger = logging.getLogger(__name__)

# ==========================================
# VISTAS PRINCIPALES
# ==========================================

@login_required
def solicitar_reconsideracion(request, solicitud_id):
    """
    Vista para que el oficial solicite una reconsideración
    """
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar permisos - solo el propietario puede solicitar reconsideración
    if solicitud.propietario != request.user:
        messages.error(request, "Solo el propietario de la solicitud puede solicitar una reconsideración.")
        return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Verificar que la solicitud esté en estado rechazado o alternativa
    if solicitud.resultado_consulta not in ['Rechazado', 'Alternativa']:
        messages.error(request, "Solo se pueden reconsiderar solicitudes rechazadas o con resultado alternativo.")
        return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Obtener cotizaciones disponibles para el cliente
    cotizaciones_disponibles = []
    if solicitud.cliente and solicitud.cliente.cedulaCliente:
        cotizaciones_disponibles = Cotizacion.objects.filter(
            cedulaCliente=solicitud.cliente.cedulaCliente
        ).order_by('-created_at')
    
    if request.method == 'POST':
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                motivo = request.POST.get('motivo', '').strip()
                cotizacion_id = request.POST.get('cotizacion_id')
                
                if not motivo:
                    error_msg = "Debe proporcionar un motivo para la reconsideración."
                    if is_ajax:
                        return JsonResponse({'success': False, 'message': error_msg})
                    messages.error(request, error_msg)
                    raise ValueError("Motivo requerido")
                
                # Validar cotización seleccionada
                nueva_cotizacion = None
                usar_nueva_cotizacion = False
                if cotizacion_id:
                    try:
                        nueva_cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
                        usar_nueva_cotizacion = True
                    except:
                        error_msg = "Cotización seleccionada no válida."
                        if is_ajax:
                            return JsonResponse({'success': False, 'message': error_msg})
                        messages.error(request, error_msg)
                        raise ValueError("Cotización inválida")
                
                # Obtener información de la consulta anterior
                resultado_anterior = getattr(solicitud, 'resultado_consulta', '')
                comentario_anterior = ''
                
                # Buscar el último comentario del analista
                ultimo_comentario = solicitud.comentarios.filter(
                    tipo='analista_credito'
                ).order_by('-fecha_creacion').first()
                
                if ultimo_comentario:
                    comentario_anterior = ultimo_comentario.comentario
                
                # Calcular número de reconsideración
                numero_reconsideracion = solicitud.reconsideraciones.count() + 1
                
                # Crear la reconsideración
                reconsideracion = ReconsideracionSolicitud.objects.create(
                    solicitud=solicitud,
                    numero_reconsideracion=numero_reconsideracion,
                    solicitada_por=request.user,
                    motivo=motivo,
                    cotizacion_original=solicitud.cotizacion,
                    cotizacion_nueva=nueva_cotizacion,
                    usar_nueva_cotizacion=usar_nueva_cotizacion,
                    resultado_consulta_anterior=resultado_anterior,
                    comentario_consulta_anterior=comentario_anterior,
                )
                
                # Actualizar la cotización de la solicitud si se seleccionó una nueva
                if usar_nueva_cotizacion and nueva_cotizacion:
                    solicitud.cotizacion = nueva_cotizacion
                
                # Mover la solicitud a la etapa de consulta
                # Buscar específicamente la etapa "Consulta" (no "Resultado Consulta")
                logger.info(f"Buscando etapa de consulta para pipeline: {solicitud.pipeline.nombre}")
                
                # Primero, listar todas las etapas que contienen 'consulta' para debug
                etapas_con_consulta = Etapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    nombre__icontains='consulta'
                ).values_list('nombre', flat=True)
                logger.info(f"Etapas encontradas con 'consulta': {list(etapas_con_consulta)}")
                
                etapa_consulta = Etapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    nombre__iexact='consulta'
                ).first()
                
                # Si no encuentra con nombre exacto, probar variaciones comunes
                if not etapa_consulta:
                    etapa_consulta = Etapa.objects.filter(
                        pipeline=solicitud.pipeline,
                        nombre__in=['Consulta', 'consulta', 'CONSULTA']
                    ).first()
                
                # Si aún no encuentra, buscar que empiece con "Consulta" pero no sea "Resultado Consulta"
                if not etapa_consulta:
                    etapa_consulta = Etapa.objects.filter(
                        pipeline=solicitud.pipeline,
                        nombre__istartswith='consulta'
                    ).exclude(
                        nombre__icontains='resultado'
                    ).first()
                
                if etapa_consulta:
                    logger.info(f"Etapa de consulta seleccionada: '{etapa_consulta.nombre}'")
                else:
                    logger.error(f"No se encontró etapa de consulta válida. Etapas disponibles: {list(etapas_con_consulta)}")
                
                if not etapa_consulta:
                    messages.error(request, "No se encontró la etapa de consulta en el pipeline.")
                    raise ValueError("Etapa consulta no encontrada")
                
                # Guardar estado anterior para historial
                etapa_anterior = solicitud.etapa_actual
                subestado_anterior = solicitud.subestado_actual
                
                # Actualizar solicitud
                solicitud.etapa_actual = etapa_consulta
                solicitud.subestado_actual = etapa_consulta.subestados.first()  # Primer subestado de consulta
                solicitud.fecha_ultima_actualizacion = timezone.now()
                
                # Marcar como reconsideración
                solicitud.es_reconsideracion = True
                
                # También agregar etiqueta visual
                etiquetas_actuales = solicitud.etiquetas_oficial or ''
                if 'Reconsideración' not in etiquetas_actuales:
                    solicitud.etiquetas_oficial = f"{etiquetas_actuales}, Reconsideración".strip(', ')
                
                solicitud.save()
                
                # Crear entrada en historial
                if etapa_anterior:
                    # Cerrar historial anterior
                    historial_anterior = HistorialSolicitud.objects.filter(
                        solicitud=solicitud,
                        fecha_fin__isnull=True
                    ).first()
                    
                    if historial_anterior:
                        historial_anterior.fecha_fin = timezone.now()
                        historial_anterior.save()
                
                # Crear nuevo historial
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa=etapa_consulta,
                    subestado=solicitud.subestado_actual,
                    usuario_responsable=request.user,
                    fecha_inicio=timezone.now()
                )
                
                # Crear comentario de sistema
                SolicitudComentario.objects.create(
                    solicitud=solicitud,
                    usuario=request.user,
                    comentario=f"Solicitud enviada para reconsideración #{numero_reconsideracion}. Motivo: {motivo}",
                    tipo='general'
                )
                
                # Notificar cambio
                notify_solicitud_change(solicitud, 'reconsideracion_solicitada', request.user)
                
                # Enviar email al equipo de consulta
                enviar_notificacion_reconsideracion(reconsideracion)
                
                success_msg = f"Reconsideración #{numero_reconsideracion} enviada exitosamente."
                
                if is_ajax:
                    return JsonResponse({
                        'success': True, 
                        'message': success_msg,
                        'numero_reconsideracion': numero_reconsideracion
                    })
                
                messages.success(request, success_msg)
                return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
                
        except Exception as e:
            logger.error(f"Error al solicitar reconsideración: {str(e)}")
            error_msg = f"Error al procesar la reconsideración: {str(e)}"
            
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg})
            
            messages.error(request, error_msg)
    
    context = {
        'solicitud': solicitud,
        'cotizaciones_disponibles': cotizaciones_disponibles,
        'numero_proxima_reconsideracion': solicitud.reconsideraciones.count() + 1,
    }
    
    return render(request, 'workflow/reconsideraciones/solicitar_reconsideracion.html', context)


@login_required
def detalle_reconsideracion_analista(request, solicitud_id):
    """
    Vista especializada para analistas que revisan reconsideraciones
    """
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud tenga reconsideraciones
    reconsideracion_actual = solicitud.reconsideraciones.filter(
        estado__in=['enviada', 'en_revision']
    ).first()
    
    if not reconsideracion_actual:
        messages.error(request, "Esta solicitud no tiene reconsideraciones pendientes.")
        return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Obtener historial de reconsideraciones
    historial_reconsideraciones = solicitud.reconsideraciones.all().order_by('-numero_reconsideracion')
    
    # Obtener análisis anteriores
    analisis_anteriores = solicitud.comentarios.filter(
        tipo='analista_credito'
    ).order_by('fecha_creacion')
    
    # Obtener participaciones de comité anteriores si existen
    participaciones_comite = []
    try:
        from .modelsWorkflow import ParticipacionComite
        participaciones_comite = ParticipacionComite.objects.filter(
            solicitud=solicitud
        ).select_related('usuario', 'nivel', 'usuario__userprofile').order_by('nivel__orden', '-fecha_modificacion')
    except ImportError:
        pass
    
    context = {
        'solicitud': solicitud,
        'reconsideracion_actual': reconsideracion_actual,
        'historial_reconsideraciones': historial_reconsideraciones,
        'analisis_anteriores': analisis_anteriores,
        'participaciones_comite': participaciones_comite,
        'es_vista_reconsideracion': True,
    }
    
    return render(request, 'workflow/reconsideraciones/detalle_analisis_reconsideracion.html', context)


@login_required
def detalle_reconsideracion_comite(request, solicitud_id):
    """
    Vista especializada para comité que revisa reconsideraciones
    """
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud tenga reconsideraciones
    reconsideracion_actual = solicitud.reconsideraciones.filter(
        estado='enviada_comite'
    ).first()
    
    if not reconsideracion_actual:
        messages.error(request, "Esta solicitud no tiene reconsideraciones en comité.")
        return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Obtener todo el historial de análisis y decisiones
    historial_completo = []
    
    # Agregar reconsideraciones
    for recon in solicitud.reconsideraciones.all().order_by('numero_reconsideracion'):
        historial_completo.append({
            'tipo': 'reconsideracion',
            'numero': recon.numero_reconsideracion,
            'fecha': recon.fecha_solicitud,
            'usuario': recon.solicitada_por,
            'motivo': recon.motivo,
            'cotizacion_cambio': recon.usar_nueva_cotizacion,
            'estado': recon.estado,
            'analista': recon.analizada_por,
            'comentario_analisis': recon.comentario_analisis,
        })
    
    # Agregar análisis de consulta
    analisis_consulta = solicitud.comentarios.filter(
        tipo='analista_credito'
    ).order_by('fecha_creacion')
    
    for analisis in analisis_consulta:
        historial_completo.append({
            'tipo': 'analisis_consulta',
            'fecha': analisis.fecha_creacion,
            'usuario': analisis.usuario,
            'comentario': analisis.comentario,
        })
    
    # Agregar participaciones de comité anteriores
    try:
        from .views_comite import obtener_participaciones_comite
        participaciones = obtener_participaciones_comite(solicitud)
        for part in participaciones:
            historial_completo.append({
                'tipo': 'participacion_comite',
                'fecha': part.fecha_participacion,
                'usuario': part.usuario,
                'nivel': part.nivel_comite.nombre,
                'resultado': part.resultado,
                'comentario': part.comentario,
            })
    except ImportError:
        pass
    
    # Ordenar cronológicamente
    historial_completo.sort(key=lambda x: x['fecha'])
    
    context = {
        'solicitud': solicitud,
        'reconsideracion_actual': reconsideracion_actual,
        'historial_completo': historial_completo,
        'es_vista_reconsideracion_comite': True,
    }
    
    return render(request, 'workflow/reconsideraciones/detalle_comite_reconsideracion.html', context)


# ==========================================
# APIs PARA RECONSIDERACIONES
# ==========================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_procesar_reconsideracion_analista(request, solicitud_id):
    """
    API para que el analista procese una reconsideración
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Obtener la reconsideración actual
        reconsideracion = solicitud.reconsideraciones.filter(
            estado__in=['enviada', 'en_revision']
        ).first()
        
        if not reconsideracion:
            return JsonResponse({
                'success': False,
                'error': 'No hay reconsideración pendiente'
            })
        
        # Handle both FormData and JSON
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # FormData from frontend
            data = request.POST
            
        decision = data.get('decision')  # 'aprobar', 'rechazar', 'enviar_comite'
        comentario = data.get('comentario', '').strip()
        
        if not decision:
            return JsonResponse({
                'success': False,
                'error': 'La decisión es obligatoria'
            })
        
        if not comentario:
            return JsonResponse({
                'success': False,
                'error': 'El comentario es obligatorio'
            })
        
        with transaction.atomic():
            # Actualizar reconsideración
            reconsideracion.analizada_por = request.user
            reconsideracion.fecha_analisis = timezone.now()
            reconsideracion.comentario_analisis = comentario
            
            if decision == 'aprobar':
                reconsideracion.estado = 'aprobada'
                # Mover solicitud a "Resultado Consulta" etapa
                etapa_resultado = Etapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    nombre__icontains='resultado'
                ).first()
                
                if etapa_resultado:
                    # Clear previous result and set as approved
                    solicitud.etapa_actual = etapa_resultado
                    solicitud.subestado_actual = etapa_resultado.subestados.filter(
                        nombre__icontains='aprobad'
                    ).first() or etapa_resultado.subestados.first()
                    solicitud.resultado_consulta = 'Aprobado'
                    solicitud.asignada_a = None  # Liberar asignación
                    solicitud.save()
                    
                    # Crear historial
                    HistorialSolicitud.objects.create(
                        solicitud=solicitud,
                        etapa=etapa_resultado,
                        subestado=solicitud.subestado_actual,
                        usuario_responsable=request.user,
                        fecha_inicio=timezone.now()
                    )
                
            elif decision == 'rechazar':
                reconsideracion.estado = 'rechazada'
                # Mantener en "Resultado Consulta" pero como rechazado
                etapa_resultado = Etapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    nombre__icontains='resultado'
                ).first()
                
                if etapa_resultado:
                    solicitud.etapa_actual = etapa_resultado
                    solicitud.subestado_actual = etapa_resultado.subestados.filter(
                        nombre__icontains='rechazad'
                    ).first() or etapa_resultado.subestados.first()
                    solicitud.resultado_consulta = 'Rechazado'
                    solicitud.asignada_a = None  # Liberar asignación
                    solicitud.save()
                    
                    # Crear historial
                    HistorialSolicitud.objects.create(
                        solicitud=solicitud,
                        etapa=etapa_resultado,
                        subestado=solicitud.subestado_actual,
                        usuario_responsable=request.user,
                        fecha_inicio=timezone.now()
                    )
                
            elif decision == 'enviar_comite':
                reconsideracion.estado = 'enviada_comite'
                # Mover a etapa de comité
                etapa_comite = Etapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    nombre__icontains='comité'
                ).first()
                
                if etapa_comite:
                    solicitud.etapa_actual = etapa_comite
                    solicitud.subestado_actual = etapa_comite.subestados.first()
                    solicitud.asignada_a = None  # Liberar asignación
                    solicitud.save()
                    
                    # Crear historial
                    HistorialSolicitud.objects.create(
                        solicitud=solicitud,
                        etapa=etapa_comite,
                        subestado=solicitud.subestado_actual,
                        usuario_responsable=request.user,
                        fecha_inicio=timezone.now()
                    )
            
            reconsideracion.save()
            
            # Crear comentario
            SolicitudComentario.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                comentario=f"Reconsideración #{reconsideracion.numero_reconsideracion} {decision}: {comentario}",
                tipo='analista_credito'
            )
            
            # Notificar cambio
            notify_solicitud_change(solicitud, f'reconsideracion_{decision}', request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Reconsideración procesada: {decision}',
            'redirect_url': 'workflow/bandeja-mixta/'
        })
        
    except Exception as e:
        logger.error(f"Error procesando reconsideración: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error procesando reconsideración: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def api_historial_reconsideraciones(request, solicitud_id):
    """
    API para obtener el historial completo de reconsideraciones
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        reconsideraciones = []
        for recon in solicitud.reconsideraciones.all():
            # Get cotización details
            cotizacion_original_details = None
            if recon.cotizacion_original:
                cotizacion_original_details = {
                    'id': recon.cotizacion_original.id,
                    'monto': float(recon.cotizacion_original.auxMonto2) if recon.cotizacion_original.auxMonto2 else 0,
                    'plazo': recon.cotizacion_original.plazo if hasattr(recon.cotizacion_original, 'plazo') else 0,
                    'tipo': recon.cotizacion_original.tipoPrestamo if recon.cotizacion_original.tipoPrestamo else 'personal',
                    'fecha_creacion': recon.cotizacion_original.created_at.isoformat() if hasattr(recon.cotizacion_original, 'created_at') and recon.cotizacion_original.created_at else None,
                }
            
            cotizacion_nueva_details = None
            if recon.cotizacion_nueva:
                cotizacion_nueva_details = {
                    'id': recon.cotizacion_nueva.id,
                    'monto': float(recon.cotizacion_nueva.auxMonto2) if recon.cotizacion_nueva.auxMonto2 else 0,
                    'plazo': recon.cotizacion_nueva.plazo if hasattr(recon.cotizacion_nueva, 'plazo') else 0,
                    'tipo': recon.cotizacion_nueva.tipoPrestamo if recon.cotizacion_nueva.tipoPrestamo else 'personal',
                    'fecha_creacion': recon.cotizacion_nueva.created_at.isoformat() if hasattr(recon.cotizacion_nueva, 'created_at') and recon.cotizacion_nueva.created_at else None,
                }
            
            reconsideraciones.append({
                'id': recon.id,
                'numero': recon.numero_reconsideracion,
                'fecha_solicitud': recon.fecha_solicitud.isoformat(),
                'solicitada_por': {
                    'id': recon.solicitada_por.id,
                    'nombre': recon.solicitada_por.get_full_name() or recon.solicitada_por.username,
                },
                'motivo': recon.motivo,
                'estado': recon.estado,
                'estado_display': recon.get_estado_display(),
                'usar_nueva_cotizacion': recon.usar_nueva_cotizacion,
                'cotizacion_original': cotizacion_original_details,
                'cotizacion_nueva': cotizacion_nueva_details,
                'analizada_por': {
                    'id': recon.analizada_por.id,
                    'nombre': recon.analizada_por.get_full_name() or recon.analizada_por.username,
                } if recon.analizada_por else None,
                'fecha_analisis': recon.fecha_analisis.isoformat() if recon.fecha_analisis else None,
                'comentario_analisis': recon.comentario_analisis,
                'resultado_anterior': recon.resultado_consulta_anterior,
                'comentario_anterior': recon.comentario_consulta_anterior,
                'creado_en': recon.creado_en.isoformat() if hasattr(recon, 'creado_en') and recon.creado_en else recon.fecha_solicitud.isoformat(),
                'actualizado_en': recon.actualizado_en.isoformat() if hasattr(recon, 'actualizado_en') and recon.actualizado_en else None,
            })
        
        return JsonResponse({
            'success': True,
            'reconsideraciones': reconsideraciones,
            'total': len(reconsideraciones)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_solicitar_reconsideracion(request, solicitud_id):
    """
    API para solicitar una reconsideración via AJAX
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar elegibilidad
        can_request, reason = puede_solicitar_reconsideracion(solicitud, request.user)
        if not can_request:
            return JsonResponse({
                'success': False,
                'message': reason
            })
        
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            motivo = data.get('motivo', '').strip()
            cotizacion_id = data.get('cotizacion_id')
            archivo_pdf = None
        else:
            # FormData (when uploading files)
            motivo = request.POST.get('motivo', '').strip()
            cotizacion_id = request.POST.get('cotizacion_id')
            archivo_pdf = request.FILES.get('archivo_pdf')
        
        if not motivo:
            return JsonResponse({
                'success': False,
                'message': 'Debe proporcionar un motivo para la reconsideración.'
            })
        
        # Validar archivo PDF si se proporcionó
        if archivo_pdf:
            # Validar que es un PDF
            if not archivo_pdf.name.lower().endswith('.pdf'):
                return JsonResponse({
                    'success': False,
                    'message': 'El archivo debe ser un PDF'
                })
            
            # Validar tamaño del archivo (máx 10MB)
            if archivo_pdf.size > 10 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': 'El archivo es demasiado grande (máx 10MB)'
                })
        
        # Si se especifica una cotización nueva, el archivo PDF es obligatorio
        if cotizacion_id and cotizacion_id != 'actual' and not archivo_pdf:
            return JsonResponse({
                'success': False,
                'message': 'Es obligatorio adjuntar un archivo PDF cuando seleccionas usar una cotización diferente.'
            })
        

        
        with transaction.atomic():
            # Validar cotización seleccionada
            nueva_cotizacion = None
            usar_nueva_cotizacion = False
            if cotizacion_id:
                try:
                    nueva_cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
                    # Verificar que la cotización pertenece al mismo cliente
                    if nueva_cotizacion.cedulaCliente != solicitud.cliente.cedulaCliente:
                        return JsonResponse({
                            'success': False,
                            'message': 'La cotización seleccionada no pertenece al cliente de esta solicitud.'
                        })
                    usar_nueva_cotizacion = True
                except:
                    return JsonResponse({
                        'success': False,
                        'message': 'Cotización seleccionada no válida.'
                    })
            
            # Obtener información de la consulta anterior
            resultado_anterior = getattr(solicitud, 'resultado_consulta', '')
            comentario_anterior = ''
            
            # Buscar el último comentario del analista
            ultimo_comentario = solicitud.comentarios.filter(
                tipo='analista'
            ).order_by('-fecha_creacion').first()
            
            if ultimo_comentario:
                comentario_anterior = ultimo_comentario.comentario
            
            # Calcular número de reconsideración
            numero_reconsideracion = solicitud.reconsideraciones.count() + 1
            
            # Crear la reconsideración
            reconsideracion = ReconsideracionSolicitud.objects.create(
                solicitud=solicitud,
                numero_reconsideracion=numero_reconsideracion,
                solicitada_por=request.user,
                motivo=motivo,
                cotizacion_original=solicitud.cotizacion,
                cotizacion_nueva=nueva_cotizacion,
                usar_nueva_cotizacion=usar_nueva_cotizacion,
                resultado_consulta_anterior=resultado_anterior,
                comentario_consulta_anterior=comentario_anterior,
                archivo_adjunto=archivo_pdf,  # Agregar archivo PDF
            )
            
            # Actualizar la cotización de la solicitud si se seleccionó una nueva
            if usar_nueva_cotizacion and nueva_cotizacion:
                solicitud.cotizacion = nueva_cotizacion
            
            # Buscar etapa de consulta
            etapa_consulta = Etapa.objects.filter(
                pipeline=solicitud.pipeline,
                nombre__iexact='consulta'
            ).first()
            
            if not etapa_consulta:
                etapa_consulta = Etapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    nombre__istartswith='consulta'
                ).exclude(
                    nombre__icontains='resultado'
                ).first()
            
            if not etapa_consulta:
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontró la etapa de consulta en el pipeline.'
                })
            
            # Actualizar solicitud
            etapa_anterior = solicitud.etapa_actual
            solicitud.etapa_actual = etapa_consulta
            solicitud.subestado_actual = etapa_consulta.subestados.first()
            solicitud.fecha_ultima_actualizacion = timezone.now()
            solicitud.es_reconsideracion = True
            
            # Agregar etiqueta visual
            etiquetas_actuales = solicitud.etiquetas_oficial or ''
            if 'Reconsideración' not in etiquetas_actuales:
                solicitud.etiquetas_oficial = f"{etiquetas_actuales}, Reconsideración".strip(', ')
            
            solicitud.save()
            
            # Crear entrada en historial
            if etapa_anterior:
                historial_anterior = HistorialSolicitud.objects.filter(
                    solicitud=solicitud,
                    fecha_fin__isnull=True
                ).first()
                
                if historial_anterior:
                    historial_anterior.fecha_fin = timezone.now()
                    historial_anterior.save()
            
            # Crear nuevo historial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=etapa_consulta,
                subestado=solicitud.subestado_actual,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now()
            )
            
            # Crear comentario de sistema
            SolicitudComentario.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                comentario=f"Solicitud enviada para reconsideración #{numero_reconsideracion}. Motivo: {motivo}",
                tipo='general'
            )
            
            # Notificar cambio
            notify_solicitud_change(solicitud, 'reconsideracion_solicitada', request.user)
            
            # Enviar email al equipo de consulta
            enviar_notificacion_reconsideracion(reconsideracion)
            
            return JsonResponse({
                'success': True,
                'message': f'Reconsideración #{numero_reconsideracion} enviada exitosamente.',
                'numero_reconsideracion': numero_reconsideracion,
                'nueva_etapa': etapa_consulta.nombre,
                'solicitud_codigo': solicitud.codigo
            })
            
    except Exception as e:
        logger.error(f"Error al solicitar reconsideración via API: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar la reconsideración: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def api_cotizaciones_cliente(request, solicitud_id):
    """
    API para obtener las cotizaciones disponibles de un cliente
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Add detailed logging for debugging
        print(f"🔍 DEBUG: api_cotizaciones_cliente called for solicitud_id={solicitud_id}")
        print(f"🔍 DEBUG: Solicitud found - ID: {solicitud.id}, Codigo: {solicitud.codigo}")
        
        if not solicitud.cliente:
            print(f"❌ DEBUG: No cliente associated with solicitud {solicitud_id}")
            return JsonResponse({
                'success': False,
                'message': 'La solicitud no tiene cliente asociado',
                'cotizaciones': []
            })
            
        if not solicitud.cliente.cedulaCliente:
            print(f"❌ DEBUG: Cliente exists but no cedulaCliente for solicitud {solicitud_id}")
            return JsonResponse({
                'success': False,
                'message': 'El cliente no tiene cédula asociada',
                'cotizaciones': []
            })
        
        cliente_cedula = solicitud.cliente.cedulaCliente
        print(f"🔍 DEBUG: Cliente cedula found: {cliente_cedula}")
        
        # Count all cotizaciones first for debugging
        total_cotizaciones = Cotizacion.objects.all().count()
        print(f"🔍 DEBUG: Total cotizaciones in database: {total_cotizaciones}")
        
        # Get all cotizaciones for this cliente
        cotizaciones = Cotizacion.objects.filter(
            cedulaCliente=cliente_cedula
        ).order_by('-created_at')
        
        print(f"🔍 DEBUG: Cotizaciones filtered by cedula {cliente_cedula}: {cotizaciones.count()}")
        
        cotizaciones_data = []
        for i, cot in enumerate(cotizaciones):
            # More comprehensive data structure
            cotizacion_data = {
                'id': cot.id,
                'monto': float(cot.auxMonto2) if cot.auxMonto2 else (float(cot.montoPrestamo) if cot.montoPrestamo else 0),
                'plazo': cot.plazo if hasattr(cot, 'plazo') and cot.plazo else (cot.plazoPago if hasattr(cot, 'plazoPago') and cot.plazoPago else 0),
                'plazoPago': cot.plazoPago if hasattr(cot, 'plazoPago') and cot.plazoPago else 0,
                'tipoPrestamo': cot.tipoPrestamo if cot.tipoPrestamo else 'personal',
                'fecha_creacion': cot.created_at.isoformat() if hasattr(cot, 'created_at') and cot.created_at else '',
                'es_actual': cot.id == solicitud.cotizacion.id if solicitud.cotizacion else False,
                'nombreCliente': cot.nombreCliente if cot.nombreCliente else '',
                'cedulaCliente': cot.cedulaCliente if cot.cedulaCliente else '',
                'oficial': cot.oficial if cot.oficial else '',
                'sucursal': cot.sucursal if cot.sucursal else '',
                'tasa': float(cot.tasa) if hasattr(cot, 'tasa') and cot.tasa else None,
                # Car-specific fields for auto loans
                'marca': cot.marca if hasattr(cot, 'marca') and cot.marca else '',
                'modelo': cot.modelo if hasattr(cot, 'modelo') and cot.modelo else '',
                'yearCarro': cot.yearCarro if hasattr(cot, 'yearCarro') and cot.yearCarro else None,
                # Additional fields that might be useful
                'edad': cot.edad if hasattr(cot, 'edad') and cot.edad else None,
                'sexo': cot.sexo if hasattr(cot, 'sexo') and cot.sexo else '',
                'auxMonto2': float(cot.auxMonto2) if cot.auxMonto2 else 0,
            }
            cotizaciones_data.append(cotizacion_data)
            
            # Debug log for first few cotizaciones
            if i < 3:
                print(f"🔍 DEBUG: Cotizacion {i+1} - ID: {cot.id}, Cedula: {cot.cedulaCliente}, Cliente: {cot.nombreCliente}")
        
        print(f"✅ DEBUG: Returning {len(cotizaciones_data)} cotizaciones for cliente {cliente_cedula}")
        
        response_data = {
            'success': True,
            'message': f'Se encontraron {len(cotizaciones_data)} cotizaciones para el cliente',
            'cotizaciones': cotizaciones_data,
            'cliente_cedula': solicitud.cliente.cedulaCliente,
            'cliente_nombre': solicitud.cliente.nombreCliente if solicitud.cliente.nombreCliente else '',
            # Add debug info
            'debug_info': {
                'solicitud_id': solicitud_id,
                'total_cotizaciones_db': total_cotizaciones,
                'filtered_count': cotizaciones.count(),
                'cliente_cedula': cliente_cedula
            }
        }
        
        print(f"🔍 DEBUG: Final response - success: {response_data['success']}, count: {len(cotizaciones_data)}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"❌ DEBUG: Error in api_cotizaciones_cliente: {str(e)}")
        logger.error(f"Error obteniendo cotizaciones para solicitud {solicitud_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener cotizaciones: {str(e)}',
            'cotizaciones': []
        })


# ==========================================
# UTILIDADES PARA RECONSIDERACIONES
# ==========================================

def puede_solicitar_reconsideracion(solicitud, usuario):
    """
    Verifica si un usuario puede solicitar reconsideración para una solicitud
    """
    # Solo el propietario puede solicitar
    if solicitud.propietario != usuario:
        return False, "Solo el propietario puede solicitar reconsideración"
    
    # Verificar estado de la solicitud - debe estar en Rechazado o tener resultado Alternativa
    etapa_actual = solicitud.etapa_actual.nombre.lower() if solicitud.etapa_actual else ''
    subestado_actual = solicitud.subestado_actual.nombre.lower() if solicitud.subestado_actual else ''
    resultado_consulta = getattr(solicitud, 'resultado_consulta', '').lower()
    
    # Condiciones para poder solicitar reconsideración:
    # 1. Etapa "Rechazado" o etapa "Resultado Consulta" con subestado "Alternativa" o "Rechazado"
    # 2. O resultado_consulta sea "Rechazado" o "Alternativa"
    
    es_elegible = (
        # Etapa rechazado
        ('rechazado' in etapa_actual) or 
        # Etapa resultado consulta con subestados específicos
        ('resultado' in etapa_actual and 'consulta' in etapa_actual and 
         ('alternativa' in subestado_actual or 'rechazado' in subestado_actual)) or
        # Por resultado de consulta
        (resultado_consulta in ['rechazado', 'alternativa'])
    )
    
    if not es_elegible:
        return False, f"Solo se pueden reconsiderar solicitudes rechazadas o con alternativa. Estado actual: {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa'} - {solicitud.subestado_actual.nombre if solicitud.subestado_actual else 'Sin subestado'}"
    
    # Verificar si ya hay una reconsideración en proceso
    reconsideracion_activa = solicitud.reconsideraciones.filter(
        estado__in=['enviada', 'en_revision', 'enviada_comite']
    ).exists()
    
    if reconsideracion_activa:
        return False, "Ya hay una reconsideración en proceso"
    
    return True, "Puede solicitar reconsideración"


def obtener_resumen_reconsideraciones(solicitud):
    """
    Obtiene un resumen de las reconsideraciones de una solicitud
    """
    reconsideraciones = solicitud.reconsideraciones.all()
    
    return {
        'total': reconsideraciones.count(),
        'aprobadas': reconsideraciones.filter(estado='aprobada').count(),
        'rechazadas': reconsideraciones.filter(estado='rechazada').count(),
        'en_proceso': reconsideraciones.filter(estado__in=['enviada', 'en_revision', 'enviada_comite']).count(),
        'ultima': reconsideraciones.first() if reconsideraciones.exists() else None,
    }


def crear_timeline_reconsideracion(solicitud):
    """
    Crea un timeline completo de la solicitud incluyendo reconsideraciones
    """
    eventos = []
    
    # Agregar historial general
    for hist in solicitud.historial.all().order_by('fecha_inicio'):
        eventos.append({
            'tipo': 'historial',
            'fecha': hist.fecha_inicio,
            'titulo': f"Movido a {hist.etapa.nombre}",
            'descripcion': hist.observaciones or '',
            'usuario': hist.usuario_responsable,
            'etapa': hist.etapa.nombre,
            'subestado': hist.subestado.nombre if hist.subestado else '',
        })
    
    # Agregar reconsideraciones
    for recon in solicitud.reconsideraciones.all():
        eventos.append({
            'tipo': 'reconsideracion_solicitud',
            'fecha': recon.fecha_solicitud,
            'titulo': f"Reconsideración #{recon.numero_reconsideracion} solicitada",
            'descripcion': recon.motivo,
            'usuario': recon.solicitada_por,
            'estado': recon.estado,
            'numero': recon.numero_reconsideracion,
        })
        
        if recon.fecha_analisis:
            eventos.append({
                'tipo': 'reconsideracion_analisis',
                'fecha': recon.fecha_analisis,
                'titulo': f"Reconsideración #{recon.numero_reconsideracion} analizada",
                'descripcion': recon.comentario_analisis,
                'usuario': recon.analizada_por,
                'estado': recon.estado,
                'numero': recon.numero_reconsideracion,
            })
    
    # Agregar comentarios relevantes
    for comentario in solicitud.comentarios.filter(tipo__in=['analista_credito', 'sistema']):
        eventos.append({
            'tipo': 'comentario',
            'fecha': comentario.fecha_creacion,
            'titulo': f"Comentario - {comentario.get_tipo_display()}",
            'descripción': comentario.comentario,
            'usuario': comentario.usuario,
            'tipo_comentario': comentario.tipo,
        })
    
    # Ordenar cronológicamente
    eventos.sort(key=lambda x: x['fecha'])
    
    return eventos


def enviar_notificacion_reconsideracion(reconsideracion):
    """
    Envía notificación por email cuando se solicita una reconsideración
    """
    try:
        from django.contrib.auth.models import Group
        from .views_workflow import get_site_url
        
        # Obtener usuarios del grupo de consulta
        grupo_consulta = Group.objects.filter(name__icontains='consulta').first()
        if not grupo_consulta:
            logger.warning("No se encontró el grupo de consulta para notificaciones")
            return
        
        usuarios_consulta = grupo_consulta.user_set.filter(is_active=True, email__isnull=False)
        emails_destinatarios = [user.email for user in usuarios_consulta if user.email]
        
        if not emails_destinatarios:
            logger.warning("No se encontraron emails de usuarios del grupo consulta")
            return
        
        # Preparar contexto para el template
        context = {
            'reconsideracion': reconsideracion,
            'solicitud': reconsideracion.solicitud,
            'solicitante': reconsideracion.solicitada_por,
            'site_url': get_site_url(),
            'motivo': reconsideracion.motivo,
            'numero_reconsideracion': reconsideracion.numero_reconsideracion,
            'resultado_anterior': reconsideracion.resultado_consulta_anterior,
            'usar_nueva_cotizacion': reconsideracion.usar_nueva_cotizacion,
        }
        
        # Renderizar email HTML
        html_content = render_to_string('workflow/emails/reconsideracion_solicitada.html', context)
        
        # Crear y enviar email
        subject = f"Nueva Reconsideración #{reconsideracion.numero_reconsideracion} - {reconsideracion.solicitud.codigo}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Se ha solicitado una nueva reconsideración para la solicitud {reconsideracion.solicitud.codigo}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=emails_destinatarios
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Email de reconsideración enviado para solicitud {reconsideracion.solicitud.codigo}")
        
    except Exception as e:
        logger.error(f"Error enviando email de reconsideración: {str(e)}")
