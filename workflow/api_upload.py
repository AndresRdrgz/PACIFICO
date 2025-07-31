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


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_upload_documento_modal(request, solicitud_id):
    """
    API específica para subir/reemplazar documentos desde el modal mejorado
    Maneja tanto upload nuevo como reemplazo de documentos existentes
    """
    from django.conf import settings
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    from .models import CalificacionDocumentoBackoffice
    
    try:
        # Obtener datos del request
        documento_id = request.POST.get('documento_id')
        documento_nombre = request.POST.get('documento_nombre', 'Documento')
        action = request.POST.get('action', 'upload')  # 'upload' o 'replace'
        uploaded_file = request.FILES.get('archivo')
        
        logger.info(f"Modal upload request - solicitud_id: {solicitud_id}, documento_id: {documento_id}, action: {action}")
        
        # Validar datos requeridos
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
        
        # Validar permisos - similar a la función original
        if not (request.user.is_superuser or 
                solicitud.asignada_a == request.user or
                solicitud.creada_por == request.user or
                getattr(solicitud, 'propietario', None) == request.user or
                request.user.groups.filter(name__in=['Admins', 'Analistas', 'Oficiales']).exists()):
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
        
        # Obtener o crear RequisitoSolicitud
        requisito_solicitud = None
        if documento_id:
            try:
                # Intentar encontrar por ID de RequisitoSolicitud
                requisito_solicitud = RequisitoSolicitud.objects.filter(
                    solicitud=solicitud,
                    id=documento_id
                ).first()
                
                if not requisito_solicitud:
                    # Si no se encuentra por ID, buscar por nombre del requisito
                    requisito = Requisito.objects.filter(nombre__icontains=documento_nombre).first()
                    if requisito:
                        requisito_solicitud, created = RequisitoSolicitud.objects.get_or_create(
                            solicitud=solicitud,
                            requisito=requisito,
                            defaults={'cumplido': False}
                        )
                        logger.info(f"RequisitoSolicitud {'creado' if created else 'encontrado'} por nombre: {requisito_solicitud.pk}")
                
            except Exception as e:
                logger.error(f"Error buscando RequisitoSolicitud: {e}")
                return JsonResponse({
                    'success': False,
                    'error': 'Error al buscar el documento en el sistema'
                })
        
        if not requisito_solicitud:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo encontrar o crear el requisito de solicitud'
            })
        
        # Generar nombre único para el archivo
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        try:
            # Guardar el archivo al RequisitoSolicitud
            uploaded_file.seek(0)
            
            # Si es un reemplazo, eliminar archivo anterior si existe
            if action == 'replace' and requisito_solicitud.archivo:
                try:
                    old_file_path = requisito_solicitud.archivo.path
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                        logger.info(f"Archivo anterior eliminado: {old_file_path}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo anterior: {e}")
            
            # Guardar nuevo archivo
            requisito_solicitud.archivo.save(unique_filename, uploaded_file, save=False)
            requisito_solicitud.cumplido = True
            
            # Actualizar observaciones según el tipo de acción
            if action == 'replace':
                requisito_solicitud.observaciones = f"Documento reemplazado por {request.user.get_full_name() or request.user.username}: {uploaded_file.name}"
                
                # Si había una calificación "malo", marcarla como subsanada (LÓGICA ORIGINAL)
                calificacion_mala = CalificacionDocumentoBackoffice.objects.filter(
                    requisito_solicitud=requisito_solicitud,
                    estado='malo'
                ).order_by('-fecha_calificacion').first()
                
                if calificacion_mala:
                    calificacion_mala.subsanado = True
                    calificacion_mala.subsanado_por = request.user
                    calificacion_mala.fecha_subsanado = timezone.now()
                    calificacion_mala.save()
                    logger.info(f"Calificación marcada como subsanada: {calificacion_mala.pk}")
                
                # NUEVO: Marcar subsanado_por_oficial=True - TEMPORALMENTE COMENTADO HASTA MIGRATION
                # try:
                #     CalificacionDocumentoBackoffice.objects.filter(
                #         requisito_solicitud=requisito_solicitud
                #     ).update(
                #         subsanado_por_oficial=True
                #     )
                #     logger.info(f"✅ Marcado subsanado_por_oficial=True para documento: {requisito_solicitud.requisito.nombre}")
                # except Exception as e:
                #     logger.warning(f"Error marcando subsanado_por_oficial: {e}")
                logger.info(f"🔄 Funcionalidad subsanado_por_oficial temporalmente deshabilitada - ejecutar migration primero")
                    
            else:  # action == 'upload'
                requisito_solicitud.observaciones = f"Documento subido por {request.user.get_full_name() or request.user.username}: {uploaded_file.name}"
                
                # NUEVO: Manejar pendiente_completado - TEMPORALMENTE COMENTADO HASTA MIGRATION
                # try:
                #     # Verificar si había calificación "pendiente" o si es un documento no obligatorio
                #     calificacion_pendiente = CalificacionDocumentoBackoffice.objects.filter(
                #         requisito_solicitud=requisito_solicitud,
                #         estado='pendiente'
                #     ).order_by('-fecha_calificacion').first()
                #     
                #     if calificacion_pendiente:
                #         CalificacionDocumentoBackoffice.objects.filter(
                #             requisito_solicitud=requisito_solicitud
                #         ).update(
                #             pendiente_completado=True
                #         )
                #         logger.info(f"✅ Marcado pendiente_completado=True para documento pendiente")
                # except Exception as e:
                #     logger.warning(f"Error manejando pendiente_completado: {e}")
                logger.info(f"🔄 Funcionalidad pendiente_completado temporalmente deshabilitada - ejecutar migration primero")
            
            # IMPORTANTE: Asegurar que se guarde como cumplido para que desaparezca de pendientes
            requisito_solicitud.cumplido = True
            requisito_solicitud.save()
            
            # DEBUGGING EXHAUSTIVO
            logger.info(f"✅ RequisitoSolicitud {requisito_solicitud.id} '{requisito_solicitud.requisito.nombre}' marcado como cumplido: {requisito_solicitud.cumplido}")
            logger.info(f"📁 Archivo URL: {requisito_solicitud.archivo.url if requisito_solicitud.archivo else 'NO FILE'}")
            logger.info(f"🔄 Observaciones: {requisito_solicitud.observaciones}")
            
            # Verificar que realmente se guardó
            requisito_verificacion = RequisitoSolicitud.objects.get(id=requisito_solicitud.id)
            logger.info(f"✅ VERIFICACIÓN POST-SAVE: cumplido={requisito_verificacion.cumplido}, archivo_exists={bool(requisito_verificacion.archivo)}")
            
            # Registrar en historial si existe
            try:
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa=solicitud.etapa_actual,
                    fecha_inicio=timezone.now(),
                    activo=True,
                    usuario=request.user
                )
            except Exception as e:
                logger.warning(f"No se pudo crear entrada en historial: {e}")
            
            # Notificar cambio si existe la función
            try:
                notify_solicitud_change(solicitud.id, request.user.id, f"{'Reemplazó' if action == 'replace' else 'Subió'} documento: {documento_nombre}")
            except Exception as e:
                logger.warning(f"No se pudo enviar notificación: {e}")
            
            return JsonResponse({
                'success': True,
                'message': f"Documento {'reemplazado' if action == 'replace' else 'subido'} exitosamente",
                'data': {
                    'requisito_id': requisito_solicitud.id,
                    'requisito_nombre': requisito_solicitud.requisito.nombre,
                    'archivo_url': requisito_solicitud.archivo.url if requisito_solicitud.archivo else None,
                    'cumplido': requisito_solicitud.cumplido,
                    'observaciones': requisito_solicitud.observaciones,
                    'action_performed': action
                }
            })
            
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al guardar el archivo: {str(e)}'
            })
    
    except Exception as e:
        logger.error(f"Error en upload documento modal: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        })
