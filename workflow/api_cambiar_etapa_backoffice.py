# Endpoint específico para cambiar de etapa desde backoffice
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .modelsWorkflow import Solicitud, Etapa, HistorialSolicitud
import json

@login_required
@csrf_exempt
def api_cambiar_etapa_backoffice(request, solicitud_id):
    """API específica para cambiar de etapa desde backoffice (Trámite/Subsanación)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener la solicitud
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para cambiar esta solicitud'}, status=403)
        
        # Verificar que estamos en backoffice
        if not solicitud.etapa_actual or solicitud.etapa_actual.nombre != "Back Office":
            return JsonResponse({'error': 'Esta función solo está disponible desde Back Office'}, status=400)
        
        # Obtener datos del request
        data = json.loads(request.body)
        print(f"🔍 DEBUG BACKOFFICE: Request data received: {data}")
        
        nueva_etapa_id = data.get('etapa_destino_id')
        print(f"🔍 DEBUG BACKOFFICE: Nueva etapa ID: {nueva_etapa_id}")
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de etapa requerido'}, status=400)
        
        # Obtener la nueva etapa
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Verificar que la etapa sea posterior a backoffice
        if nueva_etapa.orden <= solicitud.etapa_actual.orden:
            return JsonResponse({'error': 'Solo se puede avanzar a etapas posteriores'}, status=400)
        
        # Guardar estados anteriores para el historial
        etapa_anterior = solicitud.etapa_actual
        subestado_anterior = solicitud.subestado_actual
        
        # Cambiar a la nueva etapa
        solicitud.etapa_actual = nueva_etapa
        
        # Asignar el primer subestado de la nueva etapa (si existe)
        primer_subestado = nueva_etapa.subestados.order_by('orden').first()
        if primer_subestado:
            solicitud.subestado_actual = primer_subestado
        else:
            solicitud.subestado_actual = None
        
        # Si la nueva etapa es bandeja grupal, desenganchar la asignación
        if nueva_etapa.es_bandeja_grupal:
            solicitud.asignada_a = None
        
        # Actualizar fecha
        solicitud.fecha_ultima_actualizacion = timezone.now()
        
        # Guardar cambios
        solicitud.save()
        
        # Crear entrada en el historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=nueva_etapa,
            subestado=solicitud.subestado_actual,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        print(f"✅ DEBUG BACKOFFICE: Cambio exitoso a {nueva_etapa.nombre}")
        
        # Siempre redirigir a la bandeja mixta después de cambiar de etapa desde backoffice
        redirect_url = '/workflow/bandejas/'
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud cambiada exitosamente a {nueva_etapa.nombre}',
            'nueva_etapa': nueva_etapa.nombre,
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        print(f"❌ ERROR BACKOFFICE: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al cambiar etapa: {str(e)}'
        }, status=500)