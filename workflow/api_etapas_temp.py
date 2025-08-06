# Función temporal para api_etapas_disponibles
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .modelsWorkflow import Solicitud, Etapa

@require_GET
@csrf_exempt
def api_etapas_disponibles(request, solicitud_id):
    """Devuelve las etapas posteriores a la etapa actual de la solicitud (por orden) dentro del mismo pipeline."""
    try:
        solicitud = Solicitud.objects.select_related('etapa_actual', 'pipeline').get(id=solicitud_id)
    except Solicitud.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Solicitud no encontrada'}, status=404)

    etapa_actual = solicitud.etapa_actual
    if not etapa_actual:
        return JsonResponse({'success': False, 'error': 'La solicitud no tiene etapa actual'}, status=400)

    # Obtener etapas posteriores (orden > etapa_actual.orden) en el mismo pipeline
    etapas = Etapa.objects.filter(pipeline=solicitud.pipeline, orden__gt=etapa_actual.orden).order_by('orden')
    etapas_data = [
        {
            'id': etapa.id,
            'nombre': etapa.nombre,
            'descripcion': getattr(etapa, 'descripcion', ''),
            'orden': etapa.orden,
        }
        for etapa in etapas
    ]
    return JsonResponse({'success': True, 'etapas': etapas_data})