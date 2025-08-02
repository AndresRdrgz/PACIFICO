from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import json
try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False
from io import BytesIO
from datetime import datetime
from .models import Proyecto, Modulo, Prueba, ProyectoUsuario, ArchivoAdjunto

@login_required
def dashboard(request):
    """Dashboard principal de proyectos QA"""
    # Get projects where user is involved
    if request.user.is_superuser:
        proyectos = Proyecto.objects.all()
    else:
        proyectos = Proyecto.objects.filter(
            usuarios_invitados__usuario=request.user,
            usuarios_invitados__activo=True
        )
    
    # Get user's role in each project
    proyectos_con_rol = []
    for proyecto in proyectos:
        try:
            proyecto_usuario = proyecto.usuarios_invitados.get(usuario=request.user)
            rol = proyecto_usuario.rol
        except ProyectoUsuario.DoesNotExist:
            rol = 'admin' if request.user.is_superuser else None
        
        proyectos_con_rol.append({
            'proyecto': proyecto,
            'rol': rol
        })
    
    # Get recent test cases
    if request.user.is_superuser:
        pruebas_recientes = Prueba.objects.all()[:10]
    else:
        pruebas_recientes = Prueba.objects.filter(
            proyecto__usuarios_invitados__usuario=request.user,
            proyecto__usuarios_invitados__activo=True
        )[:10]
    
    # Statistics
    total_proyectos = len(proyectos_con_rol)
    total_pruebas = sum(p['proyecto'].total_pruebas for p in proyectos_con_rol)
    pruebas_pendientes = sum(p['proyecto'].pruebas_pendientes for p in proyectos_con_rol)
    pruebas_fallidas = sum(p['proyecto'].pruebas_fallidas for p in proyectos_con_rol)
    
    context = {
        'proyectos_con_rol': proyectos_con_rol,
        'pruebas_recientes': pruebas_recientes,
        'total_proyectos': total_proyectos,
        'total_pruebas': total_pruebas,
        'pruebas_pendientes': pruebas_pendientes,
        'pruebas_fallidas': pruebas_fallidas,
    }
    
    return render(request, 'proyectos/dashboard.html', context)

@login_required
def proyecto_list(request):
    """Lista de proyectos"""
    if request.user.is_superuser:
        proyectos = Proyecto.objects.all()
    else:
        proyectos = Proyecto.objects.filter(
            usuarios_invitados__usuario=request.user,
            usuarios_invitados__activo=True
        )
    
    # Filtering
    estado = request.GET.get('estado')
    if estado:
        proyectos = proyectos.filter(estado=estado)
    
    # Search
    search = request.GET.get('search')
    if search:
        proyectos = proyectos.filter(
            Q(nombre__icontains=search) | 
            Q(descripcion__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(proyectos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estado_filter': estado,
        'search': search,
    }
    
    return render(request, 'proyectos/proyecto_list.html', context)

@login_required
def proyecto_detail(request, proyecto_id):
    """Detalle de un proyecto específico"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Check if user has access to this project
    if not request.user.is_superuser:
        try:
            proyecto_usuario = proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            rol_usuario = proyecto_usuario.rol
        except ProyectoUsuario.DoesNotExist:
            messages.error(request, 'No tienes acceso a este proyecto.')
            return redirect('proyectos:dashboard')
    else:
        rol_usuario = 'admin'
    
    # Get modules and test cases
    modulos = proyecto.modulos.all()
    pruebas = proyecto.pruebas.all()
    
    # Get additional filter data
    testers = User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='tester')
    desarrolladores = User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='desarrollador')
    
    # Filter pruebas by status (multiple selection)
    resultado_filter = request.GET.getlist('resultado')
    if resultado_filter:
        pruebas = pruebas.filter(resultado__in=resultado_filter)
    
    # Filter pruebas by module (multiple selection)
    modulo_filter = request.GET.getlist('modulo')
    if modulo_filter:
        pruebas = pruebas.filter(modulo_id__in=modulo_filter)
    
    # Filter pruebas by priority (multiple selection)
    prioridad_filter = request.GET.getlist('prioridad')
    if prioridad_filter:
        pruebas = pruebas.filter(prioridad__in=prioridad_filter)
    
    # Filter pruebas by tester (multiple selection)
    tester_filter = request.GET.getlist('tester')
    if tester_filter:
        # Handle "sin_asignar" (unassigned) filter
        if 'sin_asignar' in tester_filter:
            # Remove 'sin_asignar' from the list and get the remaining tester IDs
            tester_ids = [tid for tid in tester_filter if tid != 'sin_asignar']
            
            # Create Q objects for the filter
            q_objects = Q()
            
            # Add filter for unassigned tests (tester is None)
            q_objects |= Q(tester__isnull=True)
            
            # Add filter for assigned testers if any
            if tester_ids:
                q_objects |= Q(tester_id__in=tester_ids)
            
            pruebas = pruebas.filter(q_objects)
        else:
            # Normal filter without "sin_asignar"
            pruebas = pruebas.filter(tester_id__in=tester_filter)
    
    # Filter pruebas by desarrollador (multiple selection)
    desarrollador_filter = request.GET.getlist('desarrollador')
    if desarrollador_filter:
        if 'sin_asignar' in desarrollador_filter:
            desarrollador_ids = [did for did in desarrollador_filter if did != 'sin_asignar']
            q_objects = Q()
            q_objects |= Q(desarrollador__isnull=True)  # Filter for unassigned tests
            if desarrollador_ids:
                q_objects |= Q(desarrollador_id__in=desarrollador_ids)  # Combine with specific developers
            pruebas = pruebas.filter(q_objects)
        else:
            pruebas = pruebas.filter(desarrollador_id__in=desarrollador_filter)
    
    # Filter pruebas by assigned user (role-based filtering)
    if rol_usuario == 'tester':
        pruebas = pruebas.filter(tester=request.user)
    elif rol_usuario == 'desarrollador':
        pruebas = pruebas.filter(desarrollador=request.user)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', '-fecha_creacion')
    sort_order = request.GET.get('order', 'desc')
    
    # Validate sort field to prevent injection
    allowed_sort_fields = {
        'titulo': 'titulo',
        'modulo': 'modulo__nombre',
        'prioridad': 'prioridad',
        'resultado': 'resultado',
        'tester': 'tester__first_name',
        'desarrollador': 'desarrollador__first_name',
        'fecha_creacion': 'fecha_creacion',
        'fecha_ejecucion': 'fecha_ejecucion',
        'fecha_resolucion': 'fecha_resolucion',
    }
    
    if sort_by in allowed_sort_fields:
        sort_field = allowed_sort_fields[sort_by]
        if sort_order == 'asc':
            pruebas = pruebas.order_by(sort_field)
        else:
            pruebas = pruebas.order_by(f'-{sort_field}')
    else:
        # Default sorting
        pruebas = pruebas.order_by('-fecha_creacion')
    
    # Pagination
    paginator = Paginator(pruebas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'proyecto': proyecto,
        'modulos': modulos,
        'page_obj': page_obj,
        'rol_usuario': rol_usuario,
        'testers': testers,
        'desarrolladores': desarrolladores,
        'resultado_filter': resultado_filter,
        'modulo_filter': modulo_filter,
        'prioridad_filter': prioridad_filter,
        'tester_filter': tester_filter,
        'desarrollador_filter': desarrollador_filter,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    
    return render(request, 'proyectos/proyecto_detail.html', context)

@login_required
def prueba_detail(request, prueba_id):
    """Detalle de una prueba específica"""
    prueba = get_object_or_404(Prueba, id=prueba_id)
    
    # Check if user has access to this test case
    if not request.user.is_superuser:
        try:
            proyecto_usuario = prueba.proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            rol_usuario = proyecto_usuario.rol
        except ProyectoUsuario.DoesNotExist:
            messages.error(request, 'No tienes acceso a esta prueba.')
            return redirect('proyectos:dashboard')
    else:
        rol_usuario = 'admin'
    
    context = {
        'prueba': prueba,
        'rol_usuario': rol_usuario,
    }
    
    return render(request, 'proyectos/prueba_detail.html', context)

@login_required
def prueba_create(request, proyecto_id):
    """Crear nueva prueba"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Check if user has access to this project
    if not request.user.is_superuser:
        try:
            proyecto_usuario = proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            if proyecto_usuario.rol != 'tester':
                messages.error(request, 'Solo los testers pueden crear pruebas.')
                return redirect('proyectos:proyecto_detail', proyecto_id=proyecto.id)
        except ProyectoUsuario.DoesNotExist:
            messages.error(request, 'No tienes acceso a este proyecto.')
            return redirect('proyectos:dashboard')
    
    if request.method == 'POST':
        # Get form data
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        modulo_id = request.POST.get('modulo')
        prioridad = request.POST.get('prioridad', 'media')
        resultado = request.POST.get('resultado', 'pendiente')
        pasos_prueba = request.POST.get('pasos_prueba')
        resultado_esperado = request.POST.get('resultado_esperado')
        tester_id = request.POST.get('tester')
        desarrollador_id = request.POST.get('desarrollador')
        comentarios = request.POST.get('comentarios', '')
        
        # Validate required fields
        if not all([titulo, descripcion, modulo_id, pasos_prueba, resultado_esperado]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
            return render(request, 'proyectos/prueba_form.html', {
                'proyecto': proyecto,
                'modulos': proyecto.modulos.all(),
                'usuarios_tester': User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='tester'),
                'usuarios_desarrollador': User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='desarrollador'),
            })
        
        try:
            # Get the module
            modulo = proyecto.modulos.get(id=modulo_id)
            
            # Get tester and developer if specified
            tester = None
            if tester_id:
                tester = User.objects.get(id=tester_id)
            
            desarrollador = None
            if desarrollador_id:
                desarrollador = User.objects.get(id=desarrollador_id)
            
            # Handle multiple file uploads
            archivos_adjuntos = request.FILES.getlist('archivos_adjuntos')
            
            # Create the test case
            prueba = Prueba.objects.create(
                proyecto=proyecto,
                modulo=modulo,
                titulo=titulo,
                descripcion=descripcion,
                pasos_prueba=pasos_prueba,
                resultado_esperado=resultado_esperado,
                prioridad=prioridad,
                resultado=resultado,
                tester=tester,
                desarrollador=desarrollador,
                comentarios=comentarios
            )
            
            # Create file attachments
            for archivo in archivos_adjuntos:
                ArchivoAdjunto.objects.create(
                    prueba=prueba,
                    archivo=archivo,
                    nombre_original=archivo.name,
                    descripcion=request.POST.get(f'descripcion_{archivo.name}', ''),
                    subido_por=request.user
                )
            
            messages.success(request, f'Prueba "{prueba.titulo}" creada exitosamente.')
            return redirect('proyectos:prueba_detail', prueba_id=prueba.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear la prueba: {str(e)}')
            return render(request, 'proyectos/prueba_form.html', {
                'proyecto': proyecto,
                'modulos': proyecto.modulos.all(),
                'usuarios_tester': User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='tester'),
                'usuarios_desarrollador': User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='desarrollador'),
            })
    
    # GET request - show form
    context = {
        'proyecto': proyecto,
        'modulos': proyecto.modulos.all(),
        'usuarios_tester': User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='tester'),
        'usuarios_desarrollador': User.objects.filter(proyectos_invitado__proyecto=proyecto, proyectos_invitado__rol='desarrollador'),
    }
    
    return render(request, 'proyectos/prueba_form.html', context)

@login_required
def prueba_edit(request, prueba_id):
    """Editar prueba existente"""
    prueba = get_object_or_404(Prueba, id=prueba_id)
    
    # Check if user has access to this test case
    if not request.user.is_superuser:
        try:
            proyecto_usuario = prueba.proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            if proyecto_usuario.rol != 'tester' or prueba.tester != request.user:
                messages.error(request, 'No tienes permisos para editar esta prueba.')
                return redirect('proyectos:prueba_detail', prueba_id=prueba.id)
        except ProyectoUsuario.DoesNotExist:
            messages.error(request, 'No tienes acceso a esta prueba.')
            return redirect('proyectos:dashboard')
    
    if request.method == 'POST':
        # Get form data
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        modulo_id = request.POST.get('modulo')
        prioridad = request.POST.get('prioridad', 'media')
        resultado = request.POST.get('resultado', 'pendiente')
        pasos_prueba = request.POST.get('pasos_prueba')
        resultado_esperado = request.POST.get('resultado_esperado')
        tester_id = request.POST.get('tester')
        desarrollador_id = request.POST.get('desarrollador')
        comentarios = request.POST.get('comentarios', '')
        
        # Validate required fields
        if not all([titulo, descripcion, modulo_id, pasos_prueba, resultado_esperado]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
            return render(request, 'proyectos/prueba_form.html', {
                'prueba': prueba,
                'proyecto': prueba.proyecto,
                'modulos': prueba.proyecto.modulos.all(),
                'usuarios_tester': User.objects.filter(proyectos_invitado__proyecto=prueba.proyecto, proyectos_invitado__rol='tester'),
                'usuarios_desarrollador': User.objects.filter(proyectos_invitado__proyecto=prueba.proyecto, proyectos_invitado__rol='desarrollador'),
            })
        
        try:
            # Get the module
            modulo = prueba.proyecto.modulos.get(id=modulo_id)
            
            # Get tester and developer if specified
            tester = None
            if tester_id:
                tester = User.objects.get(id=tester_id)
            
            desarrollador = None
            if desarrollador_id:
                desarrollador = User.objects.get(id=desarrollador_id)
            
            # Handle multiple file uploads
            archivos_adjuntos = request.FILES.getlist('archivos_adjuntos')
            
            # Update the test case
            prueba.titulo = titulo
            prueba.descripcion = descripcion
            prueba.modulo = modulo
            prueba.prioridad = prioridad
            prueba.resultado = resultado
            prueba.pasos_prueba = pasos_prueba
            prueba.resultado_esperado = resultado_esperado
            prueba.tester = tester
            prueba.desarrollador = desarrollador
            prueba.comentarios = comentarios
            prueba.save()
            
            # Create new file attachments
            for archivo in archivos_adjuntos:
                ArchivoAdjunto.objects.create(
                    prueba=prueba,
                    archivo=archivo,
                    nombre_original=archivo.name,
                    descripcion=request.POST.get(f'descripcion_{archivo.name}', ''),
                    subido_por=request.user
                )
            
            messages.success(request, f'Prueba "{prueba.titulo}" actualizada exitosamente.')
            return redirect('proyectos:prueba_detail', prueba_id=prueba.id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la prueba: {str(e)}')
            return render(request, 'proyectos/prueba_form.html', {
                'prueba': prueba,
                'proyecto': prueba.proyecto,
                'modulos': prueba.proyecto.modulos.all(),
                'usuarios_tester': User.objects.filter(proyectos_invitado__proyecto=prueba.proyecto, proyectos_invitado__rol='tester'),
                'usuarios_desarrollador': User.objects.filter(proyectos_invitado__proyecto=prueba.proyecto, proyectos_invitado__rol='desarrollador'),
            })
    
    # GET request - show form
    context = {
        'prueba': prueba,
        'proyecto': prueba.proyecto,
        'modulos': prueba.proyecto.modulos.all(),
        'usuarios_tester': User.objects.filter(proyectos_invitado__proyecto=prueba.proyecto, proyectos_invitado__rol='tester'),
        'usuarios_desarrollador': User.objects.filter(proyectos_invitado__proyecto=prueba.proyecto, proyectos_invitado__rol='desarrollador'),
    }
    
    return render(request, 'proyectos/prueba_form.html', context)

@login_required
def api_proyecto_stats(request, proyecto_id):
    """API endpoint para estadísticas del proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Check if user has access
    if not request.user.is_superuser:
        try:
            proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
        except ProyectoUsuario.DoesNotExist:
            return JsonResponse({'error': 'No access'}, status=403)
    
    stats = {
        'total_pruebas': proyecto.total_pruebas,
        'pruebas_pendientes': proyecto.pruebas_pendientes,
        'pruebas_exitosas': proyecto.pruebas_exitosas,
        'pruebas_fallidas': proyecto.pruebas_fallidas,
        'pruebas_revision': proyecto.pruebas_revision,
    }
    
    return JsonResponse(stats)

@login_required
def invitar_usuario(request, proyecto_id):
    """Invitar usuario al proyecto (solo para superusuarios)"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para invitar usuarios.')
        return redirect('proyectos:proyecto_detail', proyecto_id=proyecto.id)
    
    if request.method == 'POST':
        # Get form data
        usuario_id = request.POST.get('usuario')
        rol = request.POST.get('rol')
        
        # Validate required fields
        if not usuario_id or not rol:
            messages.error(request, 'Usuario y rol son obligatorios.')
            return render(request, 'proyectos/invitar_usuario.html', {
                'proyecto': proyecto,
                'usuarios_disponibles': User.objects.exclude(
                    proyectos_invitado__proyecto=proyecto
                ).order_by('first_name', 'last_name', 'username')
            })
        
        try:
            # Get the user
            usuario = User.objects.get(id=usuario_id)
            
            # Check if user is already invited
            if ProyectoUsuario.objects.filter(proyecto=proyecto, usuario=usuario).exists():
                messages.error(request, f'El usuario {usuario.get_full_name() or usuario.username} ya está invitado a este proyecto.')
                return render(request, 'proyectos/invitar_usuario.html', {
                    'proyecto': proyecto,
                    'usuarios_disponibles': User.objects.exclude(
                        proyectos_invitado__proyecto=proyecto
                    ).order_by('first_name', 'last_name', 'username')
                })
            
            # Create the invitation
            proyecto_usuario = ProyectoUsuario.objects.create(
                proyecto=proyecto,
                usuario=usuario,
                rol=rol
            )
            
            # Send email notification
            if usuario.email:
                try:
                    context = {
                        'usuario': usuario,
                        'proyecto': proyecto,
                        'rol': proyecto_usuario.get_rol_display(),
                        'invitado_por': request.user.get_full_name() or request.user.username,
                        'fecha_invitacion': timezone.now().strftime("%d/%m/%Y %H:%M"),
                        'proyecto_url': request.build_absolute_uri(f'/proyectos/proyecto/{proyecto.id}/'),
                    }
                    
                    # Render email templates
                    subject = f'Invitación al Proyecto QA: {proyecto.nombre}'
                    html_message = render_to_string('proyectos/emails/invitacion_proyecto.html', context)
                    plain_message = render_to_string('proyectos/emails/invitacion_proyecto.txt', context)
                    
                    # Send email
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[usuario.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    messages.success(request, f'Usuario {usuario.get_full_name() or usuario.username} invitado exitosamente como {proyecto_usuario.get_rol_display()}. Se ha enviado una notificación por email.')
                    
                except Exception as email_error:
                    # Log the email error but don't fail the invitation
                    print(f"Error sending invitation email: {email_error}")
                    messages.success(request, f'Usuario {usuario.get_full_name() or usuario.username} invitado exitosamente como {proyecto_usuario.get_rol_display()}. Error al enviar email de notificación.')
            else:
                messages.success(request, f'Usuario {usuario.get_full_name() or usuario.username} invitado exitosamente como {proyecto_usuario.get_rol_display()}. No se pudo enviar email de notificación (usuario sin email).')
            
            return redirect('proyectos:proyecto_detail', proyecto_id=proyecto.id)
            
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
        except Exception as e:
            messages.error(request, f'Error al invitar usuario: {str(e)}')
    
    # GET request - show form
    context = {
        'proyecto': proyecto,
        'usuarios_disponibles': User.objects.exclude(
            proyectos_invitado__proyecto=proyecto
        ).order_by('first_name', 'last_name', 'username')
    }
    
    return render(request, 'proyectos/invitar_usuario.html', context)

@login_required
def crear_modulo(request, proyecto_id):
    """Crear nuevo módulo para el proyecto (solo para superusuarios)"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para crear módulos.')
        return redirect('proyectos:proyecto_detail', proyecto_id=proyecto.id)
    
    if request.method == 'POST':
        # Get form data
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        
        # Validate required fields
        if not nombre:
            messages.error(request, 'El nombre del módulo es obligatorio.')
            return render(request, 'proyectos/crear_modulo.html', {'proyecto': proyecto})
        
        try:
            # Check if module already exists
            if Modulo.objects.filter(proyecto=proyecto, nombre=nombre).exists():
                messages.error(request, f'Ya existe un módulo con el nombre "{nombre}" en este proyecto.')
                return render(request, 'proyectos/crear_modulo.html', {'proyecto': proyecto})
            
            # Create the module
            modulo = Modulo.objects.create(
                proyecto=proyecto,
                nombre=nombre,
                descripcion=descripcion
            )
            
            messages.success(request, f'Módulo "{modulo.nombre}" creado exitosamente.')
            return redirect('proyectos:proyecto_detail', proyecto_id=proyecto.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el módulo: {str(e)}')
            return render(request, 'proyectos/crear_modulo.html', {'proyecto': proyecto})
    
    # GET request - show form
    return render(request, 'proyectos/crear_modulo.html', {'proyecto': proyecto})

@login_required
def proyecto_create(request):
    """Crear nuevo proyecto (solo para superusuarios)"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para crear proyectos.')
        return redirect('proyectos:dashboard')
    
    if request.method == 'POST':
        # Get form data
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado', 'activo')
        
        # Validate required fields
        if not nombre or not descripcion:
            messages.error(request, 'El nombre y la descripción son obligatorios.')
            return render(request, 'proyectos/proyecto_form.html')
        
        try:
            # Create the project
            proyecto = Proyecto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                estado=estado,
                creado_por=request.user
            )
            
            messages.success(request, f'Proyecto "{proyecto.nombre}" creado exitosamente.')
            return redirect('proyectos:proyecto_detail', proyecto_id=proyecto.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el proyecto: {str(e)}')
            return render(request, 'proyectos/proyecto_form.html')
    
    # GET request - show form
    return render(request, 'proyectos/proyecto_form.html')

@login_required
@require_POST
@csrf_exempt
def api_update_result(request, prueba_id):
    """API endpoint para actualizar el resultado de una prueba"""
    prueba = get_object_or_404(Prueba, id=prueba_id)
    
    # Check if user has access to this test case
    if not request.user.is_superuser:
        try:
            proyecto_usuario = prueba.proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            rol_usuario = proyecto_usuario.rol
        except ProyectoUsuario.DoesNotExist:
            return JsonResponse({'error': 'No tienes acceso a esta prueba'}, status=403)
    else:
        rol_usuario = 'admin'
    
    try:
        data = json.loads(request.body)
        nuevo_resultado = data.get('resultado')
        comentario = data.get('comentario', '')
        
        if not nuevo_resultado:
            return JsonResponse({'error': 'Resultado es requerido'}, status=400)
        
        # Validate permissions based on role
        if rol_usuario == 'desarrollador':
            if nuevo_resultado != 'solicitud_revision':
                return JsonResponse({'error': 'Los desarrolladores solo pueden solicitar revisión'}, status=403)
        elif rol_usuario == 'tester':
            if nuevo_resultado not in ['exitoso', 'fallido', 'solicitud_revision']:
                return JsonResponse({'error': 'Resultado no válido'}, status=400)
        elif not request.user.is_superuser:
            return JsonResponse({'error': 'No tienes permisos para actualizar resultados'}, status=403)
        
        # Update the test case
        resultado_anterior = prueba.resultado
        prueba.resultado = nuevo_resultado
        
        # Add comment if provided
        if comentario:
            if prueba.comentarios:
                prueba.comentarios += f"\n\n--- {timezone.now().strftime('%d/%m/%Y %H:%M')} ---\n{comentario}"
            else:
                prueba.comentarios = f"--- {timezone.now().strftime('%d/%m/%Y %H:%M')} ---\n{comentario}"
        
        # Update execution date if changing from pending
        if resultado_anterior == 'pendiente' and nuevo_resultado != 'pendiente':
            prueba.fecha_ejecucion = timezone.now()
        
        # Update resolution date if marking as successful
        if nuevo_resultado == 'exitoso':
            prueba.fecha_resolucion = timezone.now()
            prueba.resuelto = True
        elif nuevo_resultado == 'fallido':
            prueba.resuelto = False
        
        prueba.save()
        
        # Send email notifications
        if nuevo_resultado == 'solicitud_revision' and (rol_usuario == 'desarrollador' or rol_usuario == 'admin'):
            print(f"🔔 Email notification triggered for revision request")
            print(f"   - Prueba: {prueba.titulo} (ID: {prueba.id})")
            print(f"   - Developer: {request.user.get_full_name() or request.user.username}")
            print(f"   - Tester: {prueba.tester.get_full_name() if prueba.tester else 'No tester assigned'}")
            
            # Notify tester about review request
            if prueba.tester and prueba.tester.email:
                print(f"   - Tester email: {prueba.tester.email}")
                try:
                    context = {
                        'prueba': prueba,
                        'desarrollador': request.user,
                        'comentario': comentario,
                        'proyecto': prueba.proyecto,
                        'fecha_solicitud': timezone.now().strftime("%d/%m/%Y %H:%M"),
                        'prueba_url': request.build_absolute_uri(f'/proyectos/prueba/{prueba.id}/'),
                    }
                    
                    subject = f'Solicitud de Revisión - Prueba: {prueba.titulo}'
                    print(f"   - Email subject: {subject}")
                    
                    html_message = render_to_string('proyectos/emails/solicitud_revision.html', context)
                    plain_message = render_to_string('proyectos/emails/solicitud_revision.txt', context)
                    print(f"   - Email templates rendered successfully")
                    print(f"   - HTML template length: {len(html_message)} characters")
                    print(f"   - Plain template length: {len(plain_message)} characters")
                    
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[prueba.tester.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    print(f"✅ Email sent successfully to {prueba.tester.email}")
                    print(f"   - From: {settings.DEFAULT_FROM_EMAIL}")
                    print(f"   - Comment included: {'Yes' if comentario else 'No'}")
                    
                except Exception as e:
                    print(f"❌ Error sending review request email: {e}")
                    print(f"   - Error type: {type(e).__name__}")
                    print(f"   - Error details: {str(e)}")
            else:
                print(f"⚠️  Cannot send email - tester not assigned or no email address")
                if not prueba.tester:
                    print(f"   - No tester assigned to this prueba")
                elif not prueba.tester.email:
                    print(f"   - Tester {prueba.tester.username} has no email address")
        else:
            print(f"📧 No email notification sent:")
            print(f"   - Resultado: {nuevo_resultado}")
            print(f"   - User role: {rol_usuario}")
            print(f"   - Condition met: {nuevo_resultado == 'solicitud_revision' and (rol_usuario == 'desarrollador' or rol_usuario == 'admin')}")
            print(f"   - Resultado is solicitud_revision: {nuevo_resultado == 'solicitud_revision'}")
            print(f"   - Role is developer or admin: {rol_usuario == 'desarrollador' or rol_usuario == 'admin'}")
        
        return JsonResponse({
            'success': True,
            'message': f'Resultado actualizado a "{prueba.get_resultado_display()}"',
            'resultado': nuevo_resultado,
            'resultado_display': prueba.get_resultado_display()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error al actualizar resultado: {str(e)}'}, status=500)

@login_required
@require_POST
@csrf_exempt
def api_mark_resolved(request, prueba_id):
    """API endpoint para marcar una prueba como resuelta (desarrolladores)"""
    prueba = get_object_or_404(Prueba, id=prueba_id)
    
    # Check if user has access and is developer
    if not request.user.is_superuser:
        try:
            proyecto_usuario = prueba.proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            if proyecto_usuario.rol != 'desarrollador':
                return JsonResponse({'error': 'Solo los desarrolladores pueden marcar como resuelto'}, status=403)
        except ProyectoUsuario.DoesNotExist:
            return JsonResponse({'error': 'No tienes acceso a esta prueba'}, status=403)
    
    try:
        data = json.loads(request.body)
        comentario = data.get('comentario', '')
        
        # Update the test case
        prueba.resultado = 'exitoso'
        prueba.resuelto = True
        prueba.fecha_resolucion = timezone.now()
        
        # Add comment if provided
        if comentario:
            if prueba.comentarios:
                prueba.comentarios += f"\n\n--- {timezone.now().strftime('%d/%m/%Y %H:%M')} (Resuelto) ---\n{comentario}"
            else:
                prueba.comentarios = f"--- {timezone.now().strftime('%d/%m/%Y %H:%M')} (Resuelto) ---\n{comentario}"
        
        prueba.save()
        
        # Notify tester about resolution
        if prueba.tester and prueba.tester.email:
            try:
                context = {
                    'prueba': prueba,
                    'desarrollador': request.user,
                    'comentario': comentario,
                    'proyecto': prueba.proyecto,
                    'fecha_resolucion': timezone.now().strftime("%d/%m/%Y %H:%M"),
                    'prueba_url': request.build_absolute_uri(f'/proyectos/prueba/{prueba.id}/'),
                }
                
                subject = f'Problema Resuelto - Prueba: {prueba.titulo}'
                html_message = render_to_string('proyectos/emails/problema_resuelto.html', context)
                plain_message = render_to_string('proyectos/emails/problema_resuelto.txt', context)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[prueba.tester.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending resolution email: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Prueba marcada como resuelta exitosamente',
            'resultado': 'exitoso',
            'resultado_display': prueba.get_resultado_display()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error al marcar como resuelto: {str(e)}'}, status=500)

@login_required
def export_pruebas_excel(request, proyecto_id):
    """Export test cases to Excel file"""
    if not XLSXWRITER_AVAILABLE:
        messages.error(request, 'La funcionalidad de exportación a Excel no está disponible. Contacte al administrador.')
        return redirect('proyectos:proyecto_detail', proyecto_id=proyecto_id)
    
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Check if user has access to this project
    if not request.user.is_superuser:
        try:
            proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
        except ProyectoUsuario.DoesNotExist:
            messages.error(request, 'No tienes acceso a este proyecto.')
            return redirect('proyectos:dashboard')
    
    # Get all test cases with filters
    pruebas = proyecto.pruebas.all()
    
    # Apply filters (multiple selection support)
    resultado_filter = request.GET.getlist('resultado')
    if resultado_filter:
        pruebas = pruebas.filter(resultado__in=resultado_filter)
    
    modulo_filter = request.GET.getlist('modulo')
    if modulo_filter:
        pruebas = pruebas.filter(modulo_id__in=modulo_filter)
    
    prioridad_filter = request.GET.getlist('prioridad')
    if prioridad_filter:
        pruebas = pruebas.filter(prioridad__in=prioridad_filter)
    
    tester_filter = request.GET.getlist('tester')
    if tester_filter:
        # Handle "sin_asignar" (unassigned) filter
        if 'sin_asignar' in tester_filter:
            # Remove 'sin_asignar' from the list and get the remaining tester IDs
            tester_ids = [tid for tid in tester_filter if tid != 'sin_asignar']
            
            # Create Q objects for the filter
            q_objects = Q()
            
            # Add filter for unassigned tests (tester is None)
            q_objects |= Q(tester__isnull=True)
            
            # Add filter for assigned testers if any
            if tester_ids:
                q_objects |= Q(tester_id__in=tester_ids)
            
            pruebas = pruebas.filter(q_objects)
        else:
            # Normal filter without "sin_asignar"
            pruebas = pruebas.filter(tester_id__in=tester_filter)
    
    desarrollador_filter = request.GET.getlist('desarrollador')
    if desarrollador_filter:
        if 'sin_asignar' in desarrollador_filter:
            desarrollador_ids = [did for did in desarrollador_filter if did != 'sin_asignar']
            q_objects = Q()
            q_objects |= Q(desarrollador__isnull=True)  # Filter for unassigned tests
            if desarrollador_ids:
                q_objects |= Q(desarrollador_id__in=desarrollador_ids)  # Combine with specific developers
            pruebas = pruebas.filter(q_objects)
        else:
            pruebas = pruebas.filter(desarrollador_id__in=desarrollador_filter)
    
    # Apply sorting (same logic as in proyecto_detail view)
    sort_by = request.GET.get('sort', '-fecha_creacion')
    sort_order = request.GET.get('order', 'desc')
    
    # Validate sort field to prevent injection
    allowed_sort_fields = {
        'titulo': 'titulo',
        'modulo': 'modulo__nombre',
        'prioridad': 'prioridad',
        'resultado': 'resultado',
        'tester': 'tester__first_name',
        'desarrollador': 'desarrollador__first_name',
        'fecha_creacion': 'fecha_creacion',
        'fecha_ejecucion': 'fecha_ejecucion',
        'fecha_resolucion': 'fecha_resolucion',
    }
    
    if sort_by in allowed_sort_fields:
        sort_field = allowed_sort_fields[sort_by]
        if sort_order == 'asc':
            pruebas = pruebas.order_by(sort_field)
        else:
            pruebas = pruebas.order_by(f'-{sort_field}')
    else:
        # Default sorting
        pruebas = pruebas.order_by('-fecha_creacion')
    
    # Create Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#009c3c',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    datetime_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
    
    # Priority formats
    prioridad_critica = workbook.add_format({'bg_color': '#dc3545', 'font_color': 'white'})
    prioridad_alta = workbook.add_format({'bg_color': '#ffc107', 'font_color': 'black'})
    prioridad_media = workbook.add_format({'bg_color': '#009c3c', 'font_color': 'white'})
    prioridad_baja = workbook.add_format({'bg_color': '#6c757d', 'font_color': 'white'})
    
    # Result formats
    resultado_exitoso = workbook.add_format({'bg_color': '#28a745', 'font_color': 'white'})
    resultado_fallido = workbook.add_format({'bg_color': '#dc3545', 'font_color': 'white'})
    resultado_revision = workbook.add_format({'bg_color': '#ffc107', 'font_color': 'black'})
    resultado_pendiente = workbook.add_format({'bg_color': '#6c757d', 'font_color': 'white'})
    
    # Create worksheet
    worksheet = workbook.add_worksheet('Pruebas')
    
    # Set column widths
    worksheet.set_column('A:A', 40)  # Título
    worksheet.set_column('B:B', 15)  # Módulo
    worksheet.set_column('C:C', 12)  # Prioridad
    worksheet.set_column('D:D', 15)  # Resultado
    worksheet.set_column('E:E', 20)  # Tester
    worksheet.set_column('F:F', 20)  # Desarrollador
    worksheet.set_column('G:G', 12)  # Fecha Creación
    worksheet.set_column('H:H', 12)  # Fecha Ejecución
    worksheet.set_column('I:I', 12)  # Fecha Resolución
    worksheet.set_column('J:J', 50)  # Descripción
    worksheet.set_column('K:K', 50)  # Pasos
    worksheet.set_column('L:L', 50)  # Resultado Esperado
    worksheet.set_column('M:M', 30)  # Comentarios
    
    # Write headers
    headers = [
        'Título', 'Módulo', 'Prioridad', 'Resultado', 'Tester', 'Desarrollador',
        'Fecha Creación', 'Fecha Ejecución', 'Fecha Resolución', 'Descripción',
        'Pasos de la Prueba', 'Resultado Esperado', 'Comentarios'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Write data
    for row, prueba in enumerate(pruebas, start=1):
        col = 0
        
        # Título
        worksheet.write(row, col, prueba.titulo)
        col += 1
        
        # Módulo
        worksheet.write(row, col, prueba.modulo.nombre)
        col += 1
        
        # Prioridad
        prioridad_text = prueba.get_prioridad_display()
        prioridad_format = None
        if prueba.prioridad == 'critica':
            prioridad_format = prioridad_critica
        elif prueba.prioridad == 'alta':
            prioridad_format = prioridad_alta
        elif prueba.prioridad == 'media':
            prioridad_format = prioridad_media
        else:
            prioridad_format = prioridad_baja
        worksheet.write(row, col, prioridad_text, prioridad_format)
        col += 1
        
        # Resultado
        resultado_text = prueba.get_resultado_display()
        resultado_format = None
        if prueba.resultado == 'exitoso':
            resultado_format = resultado_exitoso
        elif prueba.resultado == 'fallido':
            resultado_format = resultado_fallido
        elif prueba.resultado == 'solicitud_revision':
            resultado_format = resultado_revision
        else:
            resultado_format = resultado_pendiente
        worksheet.write(row, col, resultado_text, resultado_format)
        col += 1
        
        # Tester
        tester_name = prueba.tester.get_full_name() if prueba.tester else 'Sin asignar'
        worksheet.write(row, col, tester_name)
        col += 1
        
        # Desarrollador
        desarrollador_name = prueba.desarrollador.get_full_name() if prueba.desarrollador else 'Sin asignar'
        worksheet.write(row, col, desarrollador_name)
        col += 1
        
        # Fecha Creación
        worksheet.write(row, col, prueba.fecha_creacion, datetime_format)
        col += 1
        
        # Fecha Ejecución
        if prueba.fecha_ejecucion:
            worksheet.write(row, col, prueba.fecha_ejecucion, datetime_format)
        col += 1
        
        # Fecha Resolución
        if prueba.fecha_resolucion:
            worksheet.write(row, col, prueba.fecha_resolucion, datetime_format)
        col += 1
        
        # Descripción
        worksheet.write(row, col, prueba.descripcion)
        col += 1
        
        # Pasos de la Prueba
        worksheet.write(row, col, prueba.pasos_prueba)
        col += 1
        
        # Resultado Esperado
        worksheet.write(row, col, prueba.resultado_esperado)
        col += 1
        
        # Comentarios
        worksheet.write(row, col, prueba.comentarios or '')
    
    # Add summary sheet
    summary_sheet = workbook.add_worksheet('Resumen')
    
    # Summary statistics
    total_pruebas = pruebas.count()
    pruebas_exitosas = pruebas.filter(resultado='exitoso').count()
    pruebas_fallidas = pruebas.filter(resultado='fallido').count()
    pruebas_pendientes = pruebas.filter(resultado='pendiente').count()
    pruebas_revision = pruebas.filter(resultado='solicitud_revision').count()
    
    summary_data = [
        ['Métrica', 'Cantidad'],
        ['Total de Pruebas', total_pruebas],
        ['Pruebas Exitosas', pruebas_exitosas],
        ['Pruebas Fallidas', pruebas_fallidas],
        ['Pruebas Pendientes', pruebas_pendientes],
        ['En Revisión', pruebas_revision],
        ['Porcentaje de Éxito', f'{(pruebas_exitosas/total_pruebas*100):.1f}%' if total_pruebas > 0 else '0%'],
    ]
    
    for row, data in enumerate(summary_data):
        for col, value in enumerate(data):
            if row == 0:
                summary_sheet.write(row, col, value, header_format)
            else:
                summary_sheet.write(row, col, value)
    
    workbook.close()
    output.seek(0)
    
    # Create response
    filename = f"pruebas_{proyecto.nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
@require_POST
@csrf_exempt
def api_eliminar_archivo(request, archivo_id):
    """API endpoint para eliminar un archivo adjunto"""
    try:
        archivo = get_object_or_404(ArchivoAdjunto, id=archivo_id)
        prueba = archivo.prueba
        
        # Check if user has access to this test case
        if not request.user.is_superuser:
            try:
                proyecto_usuario = prueba.proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
                if proyecto_usuario.rol != 'tester' and archivo.subido_por != request.user:
                    return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este archivo.'})
            except ProyectoUsuario.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No tienes acceso a este archivo.'})
        
        # Delete the file from storage
        if archivo.archivo:
            archivo.archivo.delete()
        
        # Delete the record
        archivo.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
@csrf_exempt
def api_assign_desarrollador(request, prueba_id):
    """API endpoint para asignar un desarrollador a una prueba"""
    prueba = get_object_or_404(Prueba, id=prueba_id)
    
    # Check if user has access to this test case
    if not request.user.is_superuser:
        try:
            proyecto_usuario = prueba.proyecto.usuarios_invitados.get(usuario=request.user, activo=True)
            rol_usuario = proyecto_usuario.rol
            # Only admins and testers can assign developers
            if rol_usuario not in ['tester', 'admin']:
                return JsonResponse({'success': False, 'error': 'No tienes permisos para asignar desarrolladores'}, status=403)
        except ProyectoUsuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No tienes acceso a esta prueba'}, status=403)
    
    try:
        data = json.loads(request.body)
        desarrollador_id = data.get('desarrollador_id')
        
        # Validate desarrollador_id
        if desarrollador_id:
            try:
                desarrollador = User.objects.get(id=desarrollador_id)
                # Check if the user is actually a developer in this project
                if not request.user.is_superuser:
                    proyecto_usuario_dev = prueba.proyecto.usuarios_invitados.filter(
                        usuario=desarrollador,
                        rol='desarrollador',
                        activo=True
                    ).exists()
                    if not proyecto_usuario_dev:
                        return JsonResponse({'success': False, 'error': 'El usuario seleccionado no es un desarrollador válido para este proyecto'}, status=400)
                
                prueba.desarrollador = desarrollador
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Desarrollador no encontrado'}, status=404)
        else:
            # Remove developer assignment
            prueba.desarrollador = None
        
        prueba.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Desarrollador {"asignado" if desarrollador_id else "removido"} exitosamente',
            'desarrollador_id': desarrollador_id,
            'desarrollador_name': desarrollador.get_full_name() if desarrollador_id and desarrollador else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al asignar desarrollador: {str(e)}'}, status=500)
