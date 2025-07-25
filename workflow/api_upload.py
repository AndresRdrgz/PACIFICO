from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .modelsWorkflow import Solicitud, HistorialSolicitud, RequisitoSolicitud, Requisito
from .views_workflow import notify_solicitud_change
import os
import uuid
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_upload_documento(request):
    """
    API para subir documentos/requisitos de una solicitud
    """
    from django.conf import settings
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    try:
        # Obtener datos del request
        solicitud_id = request.POST.get('solicitud_id')
        documento_id = request.POST.get('documento_id')
        documento_nombre = request.POST.get('documento_nombre', 'Documento')
        uploaded_file = request.FILES.get('file')
        
        logger.info(f"Upload request - solicitud_id: {solicitud_id}, documento_id: {documento_id}, documento_nombre: {documento_nombre}")
        
        # Validar datos requeridos
        if not solicitud_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de solicitud requerido'
            })
        
        if not uploaded_file:
            return JsonResponse({
                'success': False,
                'error': 'Archivo requerido'
            })
        
        # Obtener solicitud
        try:
            solicitud = Solicitud.objects.get(id=solicitud_id)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Solicitud no encontrada'
            })
        
        # Validar permisos - el usuario debe poder editar la solicitud
        # o ser superuser/admin
        if not (request.user.is_superuser or 
                solicitud.asignada_a == request.user or
                solicitud.creada_por == request.user or
                request.user.groups.filter(name__in=['Admins', 'Analistas']).exists()):
            return JsonResponse({
                'success': False,
                'error': 'Sin permisos para subir documentos a esta solicitud'
            })
        
        # Validar archivo
        max_size = 10 * 1024 * 1024  # 10MB
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        
        if uploaded_file.size > max_size:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Máximo 10MB permitido.'
            })
        
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Tipo de archivo no permitido. Permitidos: {", ".join(allowed_extensions)}'
            })
        
        # Generar nombre único para el archivo
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Crear directorio si no existe
        upload_path = f"documentos/solicitud_{solicitud_id}/"
        full_upload_path = os.path.join(settings.MEDIA_ROOT, upload_path)
        try:
            os.makedirs(full_upload_path, exist_ok=True)
            logger.info(f"Directorio creado/verificado: {full_upload_path}")
        except Exception as e:
            logger.warning(f"No se pudo crear directorio: {e}")
        
        # Guardar archivo
        file_path = os.path.join(upload_path, unique_filename)
        try:
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            logger.info(f"Archivo guardado: {saved_path}")
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al guardar el archivo: {str(e)}'
            })
        
        # Crear URL completa
        file_url = os.path.join(settings.MEDIA_URL, saved_path).replace('\\', '/')
        if not file_url.startswith('http'):
            file_url = request.build_absolute_uri(file_url)
        
        # Actualizar el RequisitoSolicitud si existe
        requisito_actualizado = None
        if documento_id:
            try:
                # First, try to find RequisitoSolicitud by ID (if documento_id is actually a RequisitoSolicitud ID)
                requisito_solicitud = RequisitoSolicitud.objects.filter(
                    solicitud=solicitud,
                    id=documento_id
                ).first()
                
                logger.info(f"Searching for RequisitoSolicitud with ID: {documento_id}")
                if requisito_solicitud:
                    logger.info(f"Found RequisitoSolicitud by ID: {requisito_solicitud.pk}")
                else:
                    logger.info(f"No RequisitoSolicitud found by ID: {documento_id}")
                
                if not requisito_solicitud:
                    # If not found by ID, try to find by Requisito ID
                    try:
                        requisito = Requisito.objects.get(id=documento_id)
                        logger.info(f"Found Requisito by ID: {requisito.pk} - {requisito.nombre}")
                        requisito_solicitud, created = RequisitoSolicitud.objects.get_or_create(
                            solicitud=solicitud,
                            requisito=requisito,
                            defaults={'cumplido': False}
                        )
                        logger.info(f"Created/Found RequisitoSolicitud: {requisito_solicitud.pk} (created: {created})")
                    except Requisito.DoesNotExist:
                        logger.info(f"No Requisito found by ID: {documento_id}")
                        # If not found by Requisito ID, try to find by nombre del documento
                        requisito = Requisito.objects.filter(nombre__icontains=documento_nombre).first()
                        if requisito:
                            logger.info(f"Found Requisito by nombre: {requisito.pk} - {requisito.nombre}")
                            requisito_solicitud, created = RequisitoSolicitud.objects.get_or_create(
                                solicitud=solicitud,
                                requisito=requisito,
                                defaults={'cumplido': False}
                            )
                            logger.info(f"Created/Found RequisitoSolicitud by nombre: {requisito_solicitud.pk} (created: {created})")
                        else:
                            logger.warning(f"No Requisito found by nombre: {documento_nombre}")
                
                if requisito_solicitud:
                    logger.info(f"Found RequisitoSolicitud: {requisito_solicitud.pk} for requisito: {requisito_solicitud.requisito.nombre}")
                    
                    # Save the file directly using Django's file handling
                    try:
                        # Reset file pointer to beginning
                        uploaded_file.seek(0)
                        
                        # Save the file directly to the archivo field
                        requisito_solicitud.archivo.save(unique_filename, uploaded_file, save=False)
                        
                        requisito_solicitud.cumplido = True
                        requisito_solicitud.observaciones = f"Documento subido: {uploaded_file.name}"
                        requisito_solicitud.save()
                        requisito_actualizado = requisito_solicitud
                        logger.info(f"RequisitoSolicitud actualizado exitosamente: {requisito_solicitud.pk}")
                        
                    except Exception as e:
                        logger.error(f"Error saving file to RequisitoSolicitud: {e}")
                        # Try alternative approach
                        try:
                            # Save file to a temporary location first
                            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', unique_filename)
                            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                            
                            with open(temp_path, 'wb') as f:
                                for chunk in uploaded_file.chunks():
                                    f.write(chunk)
                            
                            # Now save to the model
                            with open(temp_path, 'rb') as f:
                                from django.core.files import File
                                django_file = File(f)
                                django_file.name = unique_filename
                                requisito_solicitud.archivo.save(unique_filename, django_file, save=False)
                            
                            requisito_solicitud.cumplido = True
                            requisito_solicitud.observaciones = f"Documento subido: {uploaded_file.name}"
                            requisito_solicitud.save()
                            requisito_actualizado = requisito_solicitud
                            logger.info(f"RequisitoSolicitud actualizado exitosamente (alternative method): {requisito_solicitud.pk}")
                            
                            # Clean up temp file
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                                
                        except Exception as e2:
                            logger.error(f"Alternative file saving method also failed: {e2}")
                            return JsonResponse({
                                'success': False,
                                'error': f'Error al guardar el archivo: {str(e2)}'
                            })
                else:
                    logger.warning(f"No se pudo encontrar o crear RequisitoSolicitud para documento_id: {documento_id}, nombre: {documento_nombre}")
                
            except Exception as e:
                logger.warning(f"No se pudo actualizar RequisitoSolicitud: {e}")
        
        # Crear entrada en el historial (solo si hay etapa actual)
        try:
            if solicitud.etapa_actual:
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa=solicitud.etapa_actual,
                    subestado=solicitud.subestado_actual,
                    usuario_responsable=request.user,
                    fecha_inicio=timezone.now()
                )
                logger.info(f"Historial creado para solicitud {solicitud_id}")
        except Exception as e:
            logger.warning(f"No se pudo crear historial: {e}")
        
        # Notificar cambio
        try:
            notify_solicitud_change(solicitud, 'documento_subido', request.user)
        except Exception as e:
            logger.warning(f"No se pudo enviar notificación: {e}")
        
        logger.info(f"Documento subido exitosamente: {uploaded_file.name} para solicitud {solicitud_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Documento subido exitosamente',
            'data': {
                'file_url': file_url,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'documento_nombre': documento_nombre,
                'fecha_subida': timezone.now().isoformat(),
                'requisito_actualizado': requisito_actualizado.pk if requisito_actualizado else None,
                'documento_id': documento_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error en upload documento: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        })
