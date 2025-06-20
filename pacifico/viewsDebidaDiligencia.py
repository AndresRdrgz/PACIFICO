from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Cliente, DebidaDiligencia
from .formsDebidaDiligencia import DebidaDiligenciaForm
import json

@login_required
@csrf_exempt
def solicitar_debida_diligencia(request, cliente_id):
    """
    View para solicitar debida diligencia de un cliente
    """
    if request.method == 'POST':
        try:
            cliente = get_object_or_404(Cliente, id=cliente_id)
            
            # Crear o obtener la debida diligencia
            diligencia, created = DebidaDiligencia.objects.get_or_create(
                cliente=cliente,
                defaults={
                    'estado': 'pendiente',
                    'solicitado_por': request.user,
                    'fecha_solicitud': timezone.now()
                }
            )
            
            if not created and diligencia.estado != 'sin_solicitar':
                return JsonResponse({
                    'success': False,
                    'message': 'La debida diligencia ya ha sido solicitada para este cliente.'
                })
            
            # Actualizar estado si ya existía
            if not created:
                diligencia.estado = 'pendiente'
                diligencia.solicitado_por = request.user
                diligencia.fecha_solicitud = timezone.now()
                diligencia.save()
            
            # Enviar email de notificación
            try:
                subject = f'Nueva Solicitud de Debida Diligencia - {cliente.nombreCliente}'
                
                # URL para el formulario de carga
                upload_url = request.build_absolute_uri(
                    reverse('debida_diligencia_upload', args=[diligencia.id])
                )
                
                message = f"""
Estimado/a Usuario,

Se ha solicitado una nueva debida diligencia para el siguiente cliente:

Cliente: {cliente.nombreCliente}
Cédula: {cliente.cedulaCliente}
Solicitado por: {request.user.get_full_name() or request.user.username}
Fecha de solicitud: {diligencia.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}

Para completar la debida diligencia, ingrese al siguiente enlace:
{upload_url}

Saludos,
Sistema Pacífico
"""
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email='aplicacion@fpacifico.com',
                    to=['makito@fpacifico.com'],
                    cc=['arodriguez@fpacifico.com', 'jacastillo@fpacifico.com'],
                )
                email.send(fail_silently=False)
                
                
                email_sent = True
            except Exception as e:
                email_sent = False
                print(f"Error enviando email: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Debida diligencia solicitada correctamente.',
                'email_sent': email_sent,
                'estado': diligencia.estado
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
def debida_diligencia_upload(request, diligencia_id):
    """
    View para cargar archivos de debida diligencia
    """
    diligencia = get_object_or_404(DebidaDiligencia, id=diligencia_id)
    
    if request.method == 'POST':
        form = DebidaDiligenciaForm(request.POST, request.FILES, instance=diligencia)
        if form.is_valid():
            diligencia = form.save(commit=False)
              # Si ambos archivos están presentes, marcar como completado
            if diligencia.archivos_completos:
                diligencia.estado = 'completado'
                diligencia.fecha_completado = timezone.now()
                diligencia.completado_por = request.user
                
                # Enviar notificación por email al usuario que solicitó la debida diligencia
                if diligencia.solicitado_por and diligencia.solicitado_por.email:
                    try:
                        subject = f'Debida Diligencia Completada - {diligencia.cliente.nombreCliente}'
                        
                        # URL para ver el perfil del cliente
                        cliente_profile_url = request.build_absolute_uri(
                            reverse('cliente_profile', args=[diligencia.cliente.id])
                        )
                        
                        message = f"""
Estimado/a {diligencia.solicitado_por.get_full_name() or diligencia.solicitado_por.username},

La debida diligencia que solicitó ha sido completada exitosamente.

Detalles del cliente:
Cliente: {diligencia.cliente.nombreCliente}
Cédula: {diligencia.cliente.cedulaCliente}
Fecha de solicitud: {diligencia.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}
Fecha de completado: {diligencia.fecha_completado.strftime('%d/%m/%Y %H:%M')}
Completado por: {diligencia.completado_por.get_full_name() or diligencia.completado_por.username}

Los archivos de debida diligencia ya están disponibles para su revisión.

Para ver los resultados, ingrese al siguiente enlace:
{cliente_profile_url}?tab=diligencia

Saludos,
Sistema Pacífico - Makito RPA
"""
                        
                        email = EmailMessage(
                            subject=subject,
                            body=message,
                            from_email='aplicacion@fpacifico.com',
                            to=[diligencia.solicitado_por.email],
                            cc=['arodriguez@fpacifico.com', 'jacastillo@fpacifico.com'],
                        )
                        email.send(fail_silently=False)
                        
                        print(f"Email de completado enviado a: {diligencia.solicitado_por.email}")
                        
                    except Exception as e:
                        print(f"Error enviando email de completado: {e}")
                        # No interrumpir el flujo si falla el email
            
            diligencia.save()
            
            messages.success(request, 'Archivos de debida diligencia guardados correctamente.')
            return redirect('debida_diligencia_upload', diligencia_id=diligencia.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DebidaDiligenciaForm(instance=diligencia)
    
    context = {
        'form': form,
        'diligencia': diligencia,
        'cliente': diligencia.cliente,
    }
    
    return render(request, 'diligencia/upload_form.html', context)


@login_required
def get_debida_diligencia_status(request, cliente_id):
    """
    API endpoint para obtener el estado de la debida diligencia de un cliente
    """
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        try:
            diligencia = DebidaDiligencia.objects.get(cliente=cliente)
            return JsonResponse({
                'success': True,
                'estado': diligencia.estado,
                'fecha_solicitud': diligencia.fecha_solicitud.isoformat() if diligencia.fecha_solicitud else None,
                'fecha_completado': diligencia.fecha_completado.isoformat() if diligencia.fecha_completado else None,
                'archivos_completos': diligencia.archivos_completos,
                'busqueda_google': diligencia.busqueda_google.url if diligencia.busqueda_google else None,
                'busqueda_registro_publico': diligencia.busqueda_registro_publico.url if diligencia.busqueda_registro_publico else None,
                'comentarios': diligencia.comentarios
            })
        except DebidaDiligencia.DoesNotExist:
            return JsonResponse({
                'success': True,
                'estado': 'sin_solicitar',
                'fecha_solicitud': None,
                'fecha_completado': None,
                'archivos_completos': False,
                'busqueda_google': None,
                'busqueda_registro_publico': None,
                'comentarios': None
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
