from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .modelsWorkflow import Solicitud, HistorialSolicitud


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_reenviar_apc_makito(request, codigo):
    """
    API para reenviar solicitud APC a Makito RPA
    Solo disponible para superusuarios
    """
    # Verificar que el usuario sea superusuario
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para realizar esta acción'
        }, status=403)
    
    try:
        # Obtener la solicitud
        solicitud = get_object_or_404(Solicitud, codigo=codigo)
        
        # Verificar que la solicitud tenga datos APC
        if not hasattr(solicitud, 'apc_no_cedula') or not solicitud.apc_no_cedula:
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud no tiene datos APC configurados'
            })
        
        if not hasattr(solicitud, 'apc_tipo_documento') or not solicitud.apc_tipo_documento:
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud no tiene tipo de documento APC configurado'
            })
        
        # Importar la función de envío de correo
        from .views_workflow import enviar_correo_apc_makito
        
        # Enviar el correo APC nuevamente
        enviar_correo_apc_makito(
            solicitud=solicitud,
            no_cedula=solicitud.apc_no_cedula,
            tipo_documento=solicitud.apc_tipo_documento,
            request=request
        )
        
        # Crear un registro en el historial si es necesario
        try:
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now(),
                observaciones=f"APC reenviado a Makito RPA por {request.user.get_full_name() or request.user.username}"
            )
        except Exception as hist_error:
            # Si falla el historial, no rompemos el flujo
            print(f"⚠️ Error al crear historial de reenvío APC: {hist_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud APC {codigo} reenviada exitosamente a Makito RPA',
            'timestamp': timezone.now().isoformat()
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except Exception as e:
        print(f"❌ Error al reenviar APC para solicitud {codigo}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })
