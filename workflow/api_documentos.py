from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .modelsWorkflow import Solicitud, RequisitoSolicitud


@login_required
@require_http_methods(["GET"])
def api_obtener_documentos_solicitud(request, solicitud_id):
    """
    API para obtener los documentos/requisitos de una solicitud
    """
    try:
        # Obtener solicitud
        try:
            solicitud = Solicitud.objects.get(id=solicitud_id)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Solicitud no encontrada'
            })
        
        # Obtener requisitos de la solicitud
        requisitos = RequisitoSolicitud.objects.filter(solicitud=solicitud).select_related('requisito')
        
        # Formatear datos
        documentos = []
        for requisito_solicitud in requisitos:
            documento = {
                'id': requisito_solicitud.pk,
                'nombre': requisito_solicitud.requisito.nombre,
                'cumplido': requisito_solicitud.cumplido,
                'observaciones': requisito_solicitud.observaciones or '',
                'url': ''
            }
            
            # Si tiene archivo, generar URL
            if requisito_solicitud.archivo:
                documento['url'] = request.build_absolute_uri(requisito_solicitud.archivo.url)
            
            documentos.append(documento)
        
        return JsonResponse({
            'success': True,
            'documentos': documentos
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })
