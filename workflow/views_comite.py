from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .modelsWorkflow import Solicitud, Etapa, ParticipacionComite, NivelComite, UsuarioNivelComite
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models
from .views_workflow import enviar_correo_pdf_resultado_consulta
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import json

# PDF Generation imports
try:
    from xhtml2pdf import pisa
    from io import BytesIO
except ImportError:
    pisa = None

@login_required
def bandeja_comite_view(request):
    """
    Renderiza la bandeja de trabajo del Comité de Crédito.
    """
    
    # Verificar permisos de acceso
    if not request.user.is_superuser:
        # Verificar si el usuario tiene PermisoBandeja para acceder al comité
        tiene_acceso = False
        
        try:
            from .modelsWorkflow import PermisoBandeja
            etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
            
            if etapa_comite:
                # Verificar permisos directos por usuario
                if PermisoBandeja.objects.filter(
                    etapa=etapa_comite,
                    usuario=request.user,
                    puede_ver=True
                ).exists():
                    tiene_acceso = True
                
                # Verificar permisos por grupos
                user_groups = request.user.groups.all()
                if user_groups.exists() and PermisoBandeja.objects.filter(
                    etapa=etapa_comite,
                    grupo__in=user_groups,
                    puede_ver=True
                ).exists():
                    tiene_acceso = True
        except Exception as e:
            messages.error(request, f'Error al verificar permisos: {str(e)}')
            
        if not tiene_acceso:
            messages.error(request, 'No tienes permisos para acceder a la bandeja del Comité de Crédito.')
            return redirect('dashboard')  # o la vista que corresponda

    # Obtener la etapa "Comité de Crédito" (usar filter().first() para evitar MultipleObjectsReturned)
    try:
        etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
        if etapa_comite:
            # Calcular la cantidad de solicitudes en la etapa del comité
            total_solicitudes = Solicitud.objects.filter(etapa_actual=etapa_comite).count()
        else:
            total_solicitudes = 0
    except Exception as e:
        # Si hay algún error, mostrar mensaje y establecer valores por defecto
        messages.error(request, f'Error al obtener las solicitudes del comité: {str(e)}')
        etapa_comite = None
        total_solicitudes = 0

    context = {
        'etapa_comite': etapa_comite,
        'total_solicitudes': total_solicitudes,
        'page_title': 'Bandeja del Comité de Crédito',
        'page_description': 'Solicitudes pendientes de revisión y aprobación por el comité.'
    }
    
    return render(request, 'workflow/bandeja_comite.html', context)


@login_required
def debug_bandeja_comite_view(request):
    """
    Debug view for troubleshooting the Comité bandeja
    """
    
    # Get the same context as the original view
    try:
        etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
        if etapa_comite:
            total_solicitudes = Solicitud.objects.filter(etapa_actual=etapa_comite).count()
        else:
            total_solicitudes = 0
    except Exception as e:
        messages.error(request, f'Error al obtener las solicitudes del comité: {str(e)}')
        etapa_comite = None
        total_solicitudes = 0

    context = {
        'etapa_comite': etapa_comite,
        'total_solicitudes': total_solicitudes,
        'page_title': 'DEBUG - Bandeja del Comité de Crédito',
        'page_description': 'Debug version for troubleshooting.'
    }
    
    return render(request, 'workflow/debug_comite.html', context)


@login_required
def detalle_solicitud_comite(request, solicitud_id):
    """
    Vista especializada para el detalle de solicitudes en el comité de crédito
    """
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud esté en etapa de comité
    if solicitud.etapa_actual.nombre != "Comité de Crédito":
        messages.error(request, 'Esta solicitud no está en la etapa del comité.')
        return redirect('workflow:bandeja_comite')
    
    # Verificar que el usuario pertenece a algún nivel del comité
    nivel_usuario = UsuarioNivelComite.objects.filter(
        usuario=request.user, 
        activo=True
    ).first()
    
    if not nivel_usuario and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para ver solicitudes del comité.')
        return redirect('workflow:bandeja_comite')
    
    # Obtener información básica de la solicitud
    cliente = solicitud.cliente if hasattr(solicitud, 'cliente') else None
    cotizacion = solicitud.cotizacion if hasattr(solicitud, 'cotizacion') else None
    historial = solicitud.historial.all().order_by('-fecha_inicio')
    # Filtrar requisitos por tipo de préstamo
    requisitos_query = solicitud.requisitos.all().select_related('requisito')
    if solicitud.cotizacion and hasattr(solicitud.cotizacion, 'tipoPrestamo'):
        # Obtener el tipo de préstamo de la cotización
        tipo_prestamo = solicitud.cotizacion.tipoPrestamo
        
        # Filtrar requisitos considerando su tipo_prestamo_aplicable
        from .modelsWorkflow import RequisitoPipeline
        requisitos_aplicables = []
        for req in requisitos_query:
            requisito_pipeline = RequisitoPipeline.objects.filter(
                pipeline=solicitud.pipeline,
                requisito=req.requisito
            ).first()
            
            # Si no existe RequisitoPipeline o si aplica para este tipo de préstamo
            if (not requisito_pipeline or 
                requisito_pipeline.tipo_prestamo_aplicable == 'todos' or
                (requisito_pipeline.tipo_prestamo_aplicable == 'personal' and tipo_prestamo == 'personal') or
                (requisito_pipeline.tipo_prestamo_aplicable == 'auto' and tipo_prestamo == 'auto')):
                requisitos_aplicables.append(req)
        
        requisitos = requisitos_aplicables
    else:
        # Si no hay cotización, mostrar todos los requisitos
        requisitos = list(requisitos_query)
    
    # Obtener participaciones del comité para esta solicitud
    participaciones = ParticipacionComite.objects.filter(
        solicitud=solicitud
    ).select_related('usuario', 'nivel', 'usuario__userprofile').order_by('nivel__orden', '-fecha_modificacion')
    
    # Obtener todos los niveles del comité ordenados por jerarquía
    niveles_comite = NivelComite.objects.all().order_by('orden')
    
    # Verificar si el usuario ya participó
    participacion_usuario = None
    if nivel_usuario:
        participacion_usuario = ParticipacionComite.objects.filter(
            solicitud=solicitud,
            usuario=request.user,
            nivel=nivel_usuario.nivel
        ).first()
    
    # Obtener solicitudes relacionadas (por cédula del cliente, excluyendo la actual)
    solicitudes_relacionadas = []
    mostrar_mensaje_sin_cliente = False
    cedula_cliente = None
    
    # Obtener cédula desde cliente o cotización
    if solicitud.cliente and solicitud.cliente.cedulaCliente:
        cedula_cliente = solicitud.cliente.cedulaCliente
    elif solicitud.cotizacion and solicitud.cotizacion.cedulaCliente:
        cedula_cliente = solicitud.cotizacion.cedulaCliente
    
    if cedula_cliente:
        # Buscar todas las solicitudes con la misma cédula (en cliente o cotización)
        solicitudes_relacionadas = Solicitud.objects.filter(
            (models.Q(cliente__cedulaCliente=cedula_cliente) | 
             models.Q(cotizacion__cedulaCliente=cedula_cliente))
        ).exclude(id=solicitud.id).select_related('cotizacion', 'cliente').order_by('-fecha_creacion')
    else:
        mostrar_mensaje_sin_cliente = True
    
    # Calcular información de progreso
    etapas_pipeline = solicitud.pipeline.etapas.all().order_by('orden')
    total_etapas = etapas_pipeline.count()
    if total_etapas > 0:
        etapa_actual_orden = solicitud.etapa_actual.orden if solicitud.etapa_actual else 0
        progreso_porcentaje = (etapa_actual_orden / total_etapas) * 100
    else:
        progreso_porcentaje = 0
    
    context = {
        'solicitud': solicitud,
        'cliente': cliente,
        'cotizacion': cotizacion,
        'historial': historial,
        'requisitos': requisitos,
        'participaciones': participaciones,
        'niveles_comite': niveles_comite,
        'nivel_usuario': nivel_usuario,
        'participacion_usuario': participacion_usuario,
        'etapas_pipeline': etapas_pipeline,
        'progreso_porcentaje': progreso_porcentaje,
        'solicitudes_relacionadas': solicitudes_relacionadas,
        'mostrar_mensaje_sin_cliente': mostrar_mensaje_sin_cliente,
        'timestamp': timezone.now().timestamp(),
    }
    
    return render(request, 'workflow/detalle_solicitud_comite.html', context)


@login_required
def api_solicitudes_procesadas_comite(request):
    """
    API para obtener solicitudes procesadas por el comité de crédito con paginación y búsqueda
    """
    
    try:
        # Verificar permisos similares a bandeja_comite_view
        if not request.user.is_superuser:
            tiene_acceso = False
            try:
                from .modelsWorkflow import PermisoBandeja
                etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
                
                if etapa_comite:
                    if PermisoBandeja.objects.filter(
                        etapa=etapa_comite,
                        usuario=request.user,
                        puede_ver=True
                    ).exists():
                        tiene_acceso = True
                    
                    user_groups = request.user.groups.all()
                    if user_groups.exists() and PermisoBandeja.objects.filter(
                        etapa=etapa_comite,
                        grupo__in=user_groups,
                        puede_ver=True
                    ).exists():
                        tiene_acceso = True
            except Exception as perm_error:
                print(f"Error verificando permisos: {perm_error}")
                
            if not tiene_acceso:
                return JsonResponse({'error': 'Sin permisos'}, status=403)

        # Parámetros de búsqueda y paginación
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        
        # Obtener solicitudes que han pasado por el comité de crédito
        # Buscamos solicitudes que tienen participaciones del comité
        solicitudes_query = Solicitud.objects.filter(
            participaciones_comite__isnull=False
        ).distinct().select_related('cliente', 'cotizacion', 'etapa_actual').prefetch_related(
            'participaciones_comite__usuario',
            'participaciones_comite__nivel'
        )
        
        # Aplicar filtros de búsqueda
        if search:
            solicitudes_query = solicitudes_query.filter(
                Q(codigo__icontains=search) |
                Q(cliente__nombreCliente__icontains=search) |
                Q(cliente__cedulaCliente__icontains=search) |
                Q(cotizacion__nombreCliente__icontains=search) |
                Q(cotizacion__cedulaCliente__icontains=search)
            )
        
        # Ordenar por fecha de modificación descendente
        solicitudes_query = solicitudes_query.order_by('-fecha_ultima_actualizacion')
        
        # Aplicar paginación
        paginator = Paginator(solicitudes_query, per_page)
        solicitudes_page = paginator.get_page(page)
        
        # Serializar datos
        solicitudes_data = []
        for solicitud in solicitudes_page:
            # Obtener información del cliente
            cliente_nombre = ""
            cliente_cedula = ""
            if solicitud.cliente:
                cliente_nombre = getattr(solicitud.cliente, 'nombreCliente', '') or ""
                cliente_cedula = getattr(solicitud.cliente, 'cedulaCliente', '') or ""
            elif solicitud.cotizacion:
                cliente_nombre = getattr(solicitud.cotizacion, 'nombreCliente', '') or ""
                cliente_cedula = getattr(solicitud.cotizacion, 'cedulaCliente', '') or ""
            
            # Obtener monto y tipo de producto
            monto = 0
            tipo_producto = ""
            if solicitud.cotizacion:
                monto = getattr(solicitud.cotizacion, 'montoSolicitado', 0) or 0
                tipo_producto = getattr(solicitud.cotizacion, 'tipoPrestamo', '')
            
            # Obtener última participación del comité
            ultima_participacion = solicitud.participaciones_comite.order_by('-fecha_modificacion').first()
            
            # Obtener estado de decisión del comité
            decision_comite = "Pendiente"
            if ultima_participacion:
                decision_comite = getattr(ultima_participacion, 'resultado', 'Pendiente') or "Pendiente"
            
            solicitudes_data.append({
                'id': solicitud.id,
                'codigo': getattr(solicitud, 'codigo', ''),
                'cliente_nombre': cliente_nombre,
                'cliente_cedula': cliente_cedula,
                'monto': float(monto),
                'tipo_producto': tipo_producto,
                'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else "",
                'fecha_creacion': solicitud.fecha_creacion.strftime('%d/%m/%Y'),
                'fecha_modificacion': solicitud.fecha_ultima_actualizacion.strftime('%d/%m/%Y %H:%M'),
                'decision_comite': decision_comite,
                'tiene_participaciones': solicitud.participaciones_comite.exists()
            })
        
        return JsonResponse({
            'solicitudes': solicitudes_data,
            'pagination': {
                'current_page': solicitudes_page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_previous': solicitudes_page.has_previous(),
                'has_next': solicitudes_page.has_next(),
                'per_page': per_page
            }
        })
        
    except Exception as e:
        print(f"Error en API solicitudes procesadas: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    """
    API para obtener solicitudes procesadas por el comité de crédito con paginación y búsqueda
    """
    
    # Verificar permisos similares a bandeja_comite_view
    if not request.user.is_superuser:
        tiene_acceso = False
        try:
            from .modelsWorkflow import PermisoBandeja
            etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
            
            if etapa_comite:
                if PermisoBandeja.objects.filter(
                    etapa=etapa_comite,
                    usuario=request.user,
                    puede_ver=True
                ).exists():
                    tiene_acceso = True
                
                user_groups = request.user.groups.all()
                if user_groups.exists() and PermisoBandeja.objects.filter(
                    etapa=etapa_comite,
                    grupo__in=user_groups,
                    puede_ver=True
                ).exists():
                    tiene_acceso = True
        except:
            pass
            
        if not tiene_acceso:
            return JsonResponse({'error': 'Sin permisos'}, status=403)

    try:
        # Parámetros de búsqueda y paginación
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        
        # Obtener solicitudes que han pasado por el comité de crédito
        # Buscamos solicitudes que tienen participaciones del comité
        solicitudes_query = Solicitud.objects.filter(
            participaciones_comite__isnull=False
        ).distinct().select_related('cliente', 'cotizacion', 'etapa_actual').prefetch_related(
            'participaciones_comite__usuario',
            'participaciones_comite__nivel'
        )
        
        # Aplicar filtros de búsqueda
        if search:
            solicitudes_query = solicitudes_query.filter(
                Q(codigo__icontains=search) |
                Q(cliente__nombreCliente__icontains=search) |
                Q(cliente__cedulaCliente__icontains=search) |
                Q(cotizacion__nombreCliente__icontains=search) |
                Q(cotizacion__cedulaCliente__icontains=search)
            )
        
        # Ordenar por fecha de modificación descendente
        solicitudes_query = solicitudes_query.order_by('-fecha_ultima_actualizacion')
        
        # Aplicar paginación
        paginator = Paginator(solicitudes_query, per_page)
        solicitudes_page = paginator.get_page(page)
        
        # Serializar datos
        solicitudes_data = []
        for solicitud in solicitudes_page:
            # Obtener información del cliente
            cliente_nombre = ""
            cliente_cedula = ""
            if solicitud.cliente:
                cliente_nombre = solicitud.cliente.nombreCliente or ""
                cliente_cedula = solicitud.cliente.cedulaCliente or ""
            elif solicitud.cotizacion:
                cliente_nombre = solicitud.cotizacion.nombreCliente or ""
                cliente_cedula = solicitud.cotizacion.cedulaCliente or ""
            
            # Obtener monto y tipo de producto
            monto = 0
            tipo_producto = ""
            if solicitud.cotizacion:
                monto = getattr(solicitud.cotizacion, 'montoSolicitado', 0) or 0
                tipo_producto = getattr(solicitud.cotizacion, 'tipoPrestamo', '')
            
            # Obtener última participación del comité
            ultima_participacion = solicitud.participaciones_comite.order_by('-fecha_modificacion').first()
            
            # Obtener estado de decisión del comité
            decision_comite = "Pendiente"
            if ultima_participacion:
                decision_comite = ultima_participacion.resultado or "Pendiente"
                decision_comite = ultima_participacion.resultado or "Pendiente"
            
            solicitudes_data.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'cliente_cedula': cliente_cedula,
                'monto': float(monto),
                'tipo_producto': tipo_producto,
                'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else "",
                'fecha_creacion': solicitud.fecha_creacion.strftime('%d/%m/%Y'),
                'fecha_modificacion': solicitud.fecha_ultima_actualizacion.strftime('%d/%m/%Y %H:%M'),
                'decision_comite': decision_comite,
                'tiene_participaciones': solicitud.participaciones_comite.exists()
            })
        
        return JsonResponse({
            'solicitudes': solicitudes_data,
            'pagination': {
                'current_page': solicitudes_page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_previous': solicitudes_page.has_previous(),
                'has_next': solicitudes_page.has_next(),
                'per_page': per_page
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def download_pdf_resultado_consulta(request, solicitud_id):
    """
    Descargar PDF de resultado de consulta para una solicitud específica
    """
    
    # Verificar permisos similares a bandeja_comite_view
    if not request.user.is_superuser:
        tiene_acceso = False
        try:
            from .modelsWorkflow import PermisoBandeja
            etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
            
            if etapa_comite:
                if PermisoBandeja.objects.filter(
                    etapa=etapa_comite,
                    usuario=request.user,
                    puede_ver=True
                ).exists():
                    tiene_acceso = True
                
                user_groups = request.user.groups.all()
                if user_groups.exists() and PermisoBandeja.objects.filter(
                    etapa=etapa_comite,
                    grupo__in=user_groups,
                    puede_ver=True
                ).exists():
                    tiene_acceso = True
        except:
            pass
            
        if not tiene_acceso:
            return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar que la solicitud tiene participaciones del comité
        if not solicitud.participaciones_comite.exists():
            return JsonResponse({'error': 'Esta solicitud no ha sido procesada por el comité'}, status=400)
        
        # Importar y usar las funciones necesarias del workflow principal
        from .models import CalificacionCampo
        
        # Preparar contexto similar al utilizado en views_workflow
        calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud).select_related('campo')
        
        # Obtener participaciones del comité
        participaciones_comite = solicitud.participaciones_comite.all().select_related(
            'usuario', 'nivel', 'usuario__userprofile'
        ).order_by('nivel__orden', '-fecha_modificacion')
        
        # Obtener comentarios del analista
        comentarios_analista = []
        analyst_comment = ""
        try:
            from .modelsWorkflow import SolicitudComentario
            comentarios = SolicitudComentario.objects.filter(
                solicitud=solicitud,
                tipo='analista'
            ).order_by('-fecha_creacion')
            
            comentarios_analista = list(comentarios)
            if comentarios_analista:
                analyst_comment = comentarios_analista[0].comentario
                analyst_comment = comentarios_analista[0].comentario
        except:
            pass
        
        # Obtener resultado de análisis si existe
        resultado_analisis = getattr(solicitud, 'resultado_analisis', '') or ""
        
        context = {
            'solicitud': solicitud,
            'calificaciones': calificaciones,
            'participaciones_comite': participaciones_comite,
            'comentarios_analista': comentarios_analista,
            'analyst_comment': analyst_comment,
            'resultado_analisis': resultado_analisis,
            'fecha_generacion': timezone.now(),
            'is_preview_mode': False,
        }
        
        # Renderizar el template HTML
        html_content = render_to_string('workflow/pdf_resultado_consulta_simple.html', context)
        
        # Generar PDF usando xhtml2pdf si está disponible
        if pisa:
            try:
                # Crear el PDF
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="resultado_consulta_{solicitud.codigo}.pdf"'
                
                # Convertir HTML a PDF
                pdf_buffer = BytesIO()
                pisa_status = pisa.pisaDocument(html_content, pdf_buffer)
                
                response.write(pdf_buffer.getvalue())
                pdf_buffer.close()
                
                return response
            except Exception as e:
                # Si hay error, devolver HTML como fallback
                response = HttpResponse(html_content, content_type='text/html')
                response['Content-Disposition'] = f'inline; filename="resultado_consulta_{solicitud.codigo}.html"'
                return response
        else:
            # Si xhtml2pdf no está disponible, devolver el HTML
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'inline; filename="resultado_consulta_{solicitud.codigo}.html"'
            return response
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 