from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Prefetch, Count
from django.core.paginator import Paginator
from .modelsWorkflow import Solicitud, Etapa, ParticipacionComite, NivelComite, UsuarioNivelComite, SolicitudEscalamientoComite, HistorialSolicitud, SolicitudComentario
from django.contrib.auth.models import User
import json

def obtener_analista_revisor(solicitud):
    """
    Obtiene información del analista que revisó el préstamo antes de llegar al comité.
    """
    # Buscar el último historial antes de llegar al comité
    historial_anterior = HistorialSolicitud.objects.filter(
        solicitud=solicitud,
        etapa__nombre__icontains='Análisis'
    ).exclude(
        etapa__nombre__iexact='Comité de Crédito'
    ).order_by('-fecha_inicio').first()
    
    # Si no hay historial de análisis, buscar cualquier historial anterior al comité
    if not historial_anterior:
        historial_anterior = HistorialSolicitud.objects.filter(
            solicitud=solicitud
        ).exclude(
            etapa__nombre__iexact='Comité de Crédito'
        ).order_by('-fecha_inicio').first()
    
    # Buscar comentarios de analista
    comentario_analista = SolicitudComentario.objects.filter(
        solicitud=solicitud,
        tipo='analista'
    ).order_by('-fecha_creacion').first()
    
    # Priorizar información del historial
    if historial_anterior and historial_anterior.usuario_responsable:
        return {
            'nombre': historial_anterior.usuario_responsable.get_full_name() or historial_anterior.usuario_responsable.username,
            'fecha': historial_anterior.fecha_inicio.strftime('%d-%m-%Y %H:%M'),
            'etapa': historial_anterior.etapa.nombre if historial_anterior.etapa else 'Etapa desconocida'
        }
    
    # Si no hay historial, usar información del comentario de analista
    if comentario_analista:
        return {
            'nombre': comentario_analista.usuario.get_full_name() or comentario_analista.usuario.username,
            'fecha': comentario_analista.fecha_creacion.strftime('%d-%m-%Y %H:%M'),
            'etapa': 'Análisis'
        }
    
    # Si no hay información específica, usar quien estuvo asignado
    if solicitud.asignada_a:
        return {
            'nombre': solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username,
            'fecha': solicitud.fecha_ultima_actualizacion.strftime('%d-%m-%Y %H:%M'),
            'etapa': 'Asignación'
        }
    
    # Fallback: usar quien creó la solicitud
    return {
        'nombre': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
        'fecha': solicitud.fecha_creacion.strftime('%d-%m-%Y %H:%M'),
        'etapa': 'Creación'
    }

@login_required
def api_solicitudes_comite(request):
    """
    API para obtener las solicitudes en la bandeja del comité con filtros y paginación.
    """
    
    # Obtener etapa del comité
    try:
        # Buscar todas las etapas con nombre "Comité de Crédito" y tomar la primera
        etapas_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").order_by('id')
        if not etapas_comite.exists():
            return JsonResponse({'success': False, 'solicitudes': [], 'total_count': 0, 'error': 'Etapa "Comité de Crédito" no encontrada.'})
        
        # Tomar la primera etapa (la más antigua)
        etapa_comite = etapas_comite.first()
        print(f"DEBUG: Usando etapa Comité de Crédito ID: {etapa_comite.id}")
    except Exception as e:
        return JsonResponse({'success': False, 'solicitudes': [], 'total_count': 0, 'error': f'Error al obtener etapa del comité: {str(e)}'})
        
    # Filtrar solicitudes en la etapa del comité
    solicitudes_qs = Solicitud.objects.filter(etapa_actual=etapa_comite)

    # Lógica de permisos (por ahora, superuser ve todo)
    if not request.user.is_superuser:
        try:
            niveles_usuario = UsuarioNivelComite.objects.filter(usuario=request.user, activo=True).values_list('nivel_id', flat=True)
            if not niveles_usuario:
                return JsonResponse({'success': False, 'solicitudes': [], 'total_count': 0}) # No pertenece a ningún nivel
        except UsuarioNivelComite.DoesNotExist:
            return JsonResponse({'success': False, 'solicitudes': [], 'total_count': 0})
    
    # Aplicar filtros
    search_query = request.GET.get('search', '')
    if search_query:
        solicitudes_qs = solicitudes_qs.filter(
            Q(codigo__icontains=search_query) |
            Q(cliente__nombreCliente__icontains=search_query) |
            Q(cliente__cedulaCliente__icontains=search_query)
        )

    # Ordenamiento
    sort_by = request.GET.get('sort_by', '-fecha_creacion')
    solicitudes_qs = solicitudes_qs.order_by(sort_by)
    
    # Paginación
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(solicitudes_qs, per_page)
    solicitudes_paginadas = paginator.get_page(page)

    # Formatear datos
    data = []
    for sol in solicitudes_paginadas:
        # Obtener información del analista que revisó el préstamo
        analista_info = obtener_analista_revisor(sol)
        
        data.append({
            'id': sol.id,
            'codigo': sol.codigo,
            'cliente_nombre': sol.cliente_nombre,
            'cliente_cedula': sol.cliente_cedula,
            'monto_formateado': sol.monto_formateado,
            'producto_descripcion': sol.producto_descripcion,
            'fecha_creacion': sol.fecha_creacion.strftime('%d-%m-%Y %H:%M'),
            'creada_por': sol.creada_por.get_full_name() or sol.creada_por.username,
            'analista_revisor': {
                'nombre': analista_info['nombre'],
                'fecha': analista_info['fecha'],
                'etapa': analista_info['etapa']
            },
        })

    return JsonResponse({
        'success': True,
        'solicitudes': data,
        'total_count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page
    })

@login_required
@require_http_methods(["POST"])
def api_participar_comite(request, solicitud_id):
    """
    API para registrar la participación de un usuario en una solicitud del comité.
    """
    try:
        data = json.loads(request.body)
        resultado = data.get('resultado')
        comentario = data.get('comentario')
        nivel_id = data.get('nivel_id')

        solicitud = Solicitud.objects.get(id=solicitud_id)
        nivel = NivelComite.objects.get(id=nivel_id)
        
        # Validar que el usuario pertenezca al nivel
        if not UsuarioNivelComite.objects.filter(usuario=request.user, nivel=nivel, activo=True).exists() and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para participar en este nivel.'}, status=403)
            
        participacion, created = ParticipacionComite.objects.update_or_create(
            solicitud=solicitud,
            nivel=nivel,
            usuario=request.user,
            defaults={'resultado': resultado, 'comentario': comentario}
        )
        
        return JsonResponse({'success': True, 'message': 'Participación registrada exitosamente.'})

    except Solicitud.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Solicitud no encontrada.'}, status=404)
    except NivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nivel de comité no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_niveles_usuario_comite(request):
    """
    API para obtener los niveles del comité disponibles para el usuario actual.
    """
    try:
        if request.user.is_superuser:
            # Los superusuarios pueden ver todos los niveles
            niveles = NivelComite.objects.all().order_by('orden')
        else:
            # Usuarios normales solo ven sus niveles asignados
            niveles = NivelComite.objects.filter(
                usuarionivecomite__usuario=request.user,
                usuarionivecomite__activo=True
            ).order_by('orden')
        
        data = []
        for nivel in niveles:
            data.append({
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden
            })
        
        return JsonResponse({'success': True, 'niveles': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_historial_participaciones(request, solicitud_id):
    """
    API para obtener el historial de participaciones de una solicitud del comité.
    """
    try:
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        participaciones = ParticipacionComite.objects.filter(
            solicitud=solicitud
        ).select_related('usuario', 'nivel').order_by('nivel__orden', '-fecha_modificacion')
        
        data = []
        for p in participaciones:
            data.append({
                'id': p.id,
                'nivel': p.nivel.nombre,
                'usuario': p.usuario.get_full_name() if p.usuario else 'Usuario no disponible',
                'resultado': p.get_resultado_display(),
                'comentario': p.comentario,
                'fecha': p.fecha_modificacion.strftime('%d-%m-%Y %H:%M')
            })
        
        return JsonResponse({'success': True, 'participaciones': data})
        
    except Solicitud.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Solicitud no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_escalar_comite(request, solicitud_id):
    """
    API para escalar una solicitud a un nivel superior del comité.
    """
    try:
        # Obtener la solicitud
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Verificar que el usuario pertenece a algún nivel del comité
        usuario_nivel = UsuarioNivelComite.objects.filter(
            usuario=request.user, 
            activo=True
        ).first()
        
        if not usuario_nivel and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para escalar solicitudes.'}, status=403)
        
        # Parsear los datos del POST
        data = json.loads(request.body)
        nivel_solicitado_id = data.get('nivel_solicitado')
        comentario = data.get('comentario', '')
        
        if not nivel_solicitado_id:
            return JsonResponse({'success': False, 'error': 'Debe especificar el nivel al que desea escalar.'}, status=400)
        
        # Obtener el nivel solicitado
        try:
            nivel_solicitado = NivelComite.objects.get(id=nivel_solicitado_id)
        except NivelComite.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Nivel del comité no encontrado.'}, status=404)
        
        # Verificar que el escalamiento sea hacia un nivel superior (menor orden = mayor jerarquía)
        if usuario_nivel and nivel_solicitado.orden >= usuario_nivel.nivel.orden:
            return JsonResponse({'success': False, 'error': 'Solo puedes escalar a niveles superiores.'}, status=400)
        
        # Verificar que no existe ya un escalamiento pendiente al mismo nivel
        escalamiento_existente = SolicitudEscalamientoComite.objects.filter(
            solicitud=solicitud,
            nivel_solicitado=nivel_solicitado,
            atendido=False
        ).exists()
        
        if escalamiento_existente:
            return JsonResponse({'success': False, 'error': 'Ya existe un escalamiento pendiente a este nivel.'}, status=400)
        
        # Crear el escalamiento
        escalamiento = SolicitudEscalamientoComite.objects.create(
            solicitud=solicitud,
            solicitado_por=request.user,
            nivel_solicitado=nivel_solicitado,
            comentario=comentario
        )
        
        # Crear una participación automática del usuario actual si no existe
        if usuario_nivel:
            participacion, created = ParticipacionComite.objects.get_or_create(
                solicitud=solicitud,
                usuario=request.user,
                nivel=usuario_nivel.nivel,
                defaults={
                    'comentario': f'Escalado a {nivel_solicitado.nombre}: {comentario}',
                    'resultado': 'OBSERVACIONES'
                }
            )
            
            if not created:
                # Actualizar la participación existente
                participacion.comentario = f'Escalado a {nivel_solicitado.nombre}: {comentario}'
                participacion.resultado = 'OBSERVACIONES'
                participacion.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Solicitud escalada exitosamente a {nivel_solicitado.nombre}.',
            'escalamiento_id': escalamiento.id
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Solicitud no encontrada.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500) 


# ==========================================
# APIs PARA GESTIÓN COMPLETA DEL COMITÉ
# ==========================================

@login_required
@require_http_methods(["GET"])
def api_obtener_niveles_comite(request):
    """
    API para obtener todos los niveles del comité
    """
    try:
        # Solo superusuarios pueden gestionar niveles
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para gestionar niveles del comité.'}, status=403)
        
        # Obtener niveles con conteo de usuarios
        niveles = NivelComite.objects.all().order_by('orden')
        
        data = []
        for nivel in niveles:
            usuarios_count = UsuarioNivelComite.objects.filter(nivel=nivel, activo=True).count()
            data.append({
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden,
                'descripcion': getattr(nivel, 'descripcion', ''),
                'usuarios_count': usuarios_count
            })
        
        return JsonResponse({'success': True, 'niveles': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_crear_nivel_comite(request):
    """
    API para crear un nuevo nivel del comité
    """
    try:
        # Solo superusuarios pueden crear niveles
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para crear niveles del comité.'}, status=403)
        
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        orden = data.get('orden')
        descripcion = data.get('descripcion', '').strip()
        
        # Validaciones
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del nivel es obligatorio.'}, status=400)
        
        if not orden or not isinstance(orden, int) or orden < 1:
            return JsonResponse({'success': False, 'error': 'El orden debe ser un número positivo.'}, status=400)
        
        # Verificar que no exista un nivel con el mismo nombre u orden
        if NivelComite.objects.filter(nombre=nombre).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un nivel con ese nombre.'}, status=400)
        
        if NivelComite.objects.filter(orden=orden).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un nivel con ese orden.'}, status=400)
        
        # Crear el nivel
        nivel = NivelComite.objects.create(
            nombre=nombre,
            orden=orden
        )
        
        # Si necesitamos descripción, la agregamos (no está en el modelo actual)
        # nivel.descripcion = descripcion
        # nivel.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Nivel creado exitosamente.',
            'nivel': {
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_actualizar_nivel_comite(request, nivel_id):
    """
    API para actualizar un nivel del comité
    """
    try:
        # Solo superusuarios pueden actualizar niveles
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para actualizar niveles del comité.'}, status=403)
        
        nivel = NivelComite.objects.get(id=nivel_id)
        data = json.loads(request.body)
        
        nombre = data.get('nombre', '').strip()
        orden = data.get('orden')
        descripcion = data.get('descripcion', '').strip()
        
        # Validaciones
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del nivel es obligatorio.'}, status=400)
        
        if not orden or not isinstance(orden, int) or orden < 1:
            return JsonResponse({'success': False, 'error': 'El orden debe ser un número positivo.'}, status=400)
        
        # Verificar que no exista otro nivel con el mismo nombre u orden
        if NivelComite.objects.filter(nombre=nombre).exclude(id=nivel_id).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe otro nivel con ese nombre.'}, status=400)
        
        if NivelComite.objects.filter(orden=orden).exclude(id=nivel_id).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe otro nivel con ese orden.'}, status=400)
        
        # Actualizar el nivel
        nivel.nombre = nombre
        nivel.orden = orden
        nivel.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Nivel actualizado exitosamente.',
            'nivel': {
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden
            }
        })
        
    except NivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nivel no encontrado.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_eliminar_nivel_comite(request, nivel_id):
    """
    API para eliminar un nivel del comité
    """
    try:
        # Solo superusuarios pueden eliminar niveles
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar niveles del comité.'}, status=403)
        
        nivel = NivelComite.objects.get(id=nivel_id)
        
        # Verificar que no tenga usuarios asignados
        usuarios_asignados = UsuarioNivelComite.objects.filter(nivel=nivel).count()
        if usuarios_asignados > 0:
            return JsonResponse({
                'success': False, 
                'error': f'No se puede eliminar el nivel porque tiene {usuarios_asignados} usuario(s) asignado(s). Primero elimine o reasigne a los usuarios.'
            }, status=400)
        
        # Eliminar el nivel
        nivel_nombre = nivel.nombre
        nivel.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Nivel "{nivel_nombre}" eliminado exitosamente.'
        })
        
    except NivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nivel no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_obtener_asignaciones_comite(request):
    """
    API para obtener todas las asignaciones de usuarios al comité
    """
    try:
        # Solo superusuarios pueden gestionar asignaciones
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para gestionar asignaciones del comité.'}, status=403)
        
        asignaciones = UsuarioNivelComite.objects.select_related('usuario', 'nivel').all().order_by('nivel__orden', 'usuario__username')
        
        data = []
        for asignacion in asignaciones:
            # Obtener información del perfil del usuario si existe
            try:
                profile_picture = asignacion.usuario.userprofile.profile_picture.url if asignacion.usuario.userprofile.profile_picture else None
            except:
                profile_picture = None
            
            data.append({
                'id': asignacion.id,
                'usuario': {
                    'id': asignacion.usuario.id,
                    'username': asignacion.usuario.username,
                    'full_name': asignacion.usuario.get_full_name(),
                    'email': asignacion.usuario.email,
                    'profile_picture': profile_picture
                },
                'nivel': {
                    'id': asignacion.nivel.id,
                    'nombre': asignacion.nivel.nombre,
                    'orden': asignacion.nivel.orden
                },
                'fecha_asignacion': asignacion.fecha_asignacion.strftime('%d-%m-%Y %H:%M'),
                'activo': asignacion.activo
            })
        
        return JsonResponse({'success': True, 'asignaciones': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_crear_asignacion_comite(request):
    """
    API para crear una nueva asignación de usuario al comité
    """
    try:
        # Solo superusuarios pueden crear asignaciones
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para crear asignaciones del comité.'}, status=403)
        
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        nivel_id = data.get('nivel_id')
        activo = data.get('activo', True)
        observaciones = data.get('observaciones', '').strip()
        
        # Validaciones
        if not usuario_id or not nivel_id:
            return JsonResponse({'success': False, 'error': 'Usuario y Nivel son obligatorios.'}, status=400)
        
        try:
            usuario = User.objects.get(id=usuario_id, is_active=True)
            nivel = NivelComite.objects.get(id=nivel_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado o inactivo.'}, status=404)
        except NivelComite.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Nivel del comité no encontrado.'}, status=404)
        
        # Verificar que el usuario no esté ya asignado a este nivel
        if UsuarioNivelComite.objects.filter(usuario=usuario, nivel=nivel).exists():
            return JsonResponse({'success': False, 'error': 'El usuario ya está asignado a este nivel del comité.'}, status=400)
        
        # Crear la asignación
        asignacion = UsuarioNivelComite.objects.create(
            usuario=usuario,
            nivel=nivel,
            activo=activo
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Usuario "{usuario.username}" asignado exitosamente al nivel "{nivel.nombre}".',
            'asignacion': {
                'id': asignacion.id,
                'usuario': usuario.username,
                'nivel': nivel.nombre,
                'activo': asignacion.activo
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_cambiar_estado_asignacion_comite(request, asignacion_id):
    """
    API para activar/desactivar una asignación de usuario al comité
    """
    try:
        # Solo superusuarios pueden cambiar estado de asignaciones
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para cambiar estado de asignaciones del comité.'}, status=403)
        
        asignacion = UsuarioNivelComite.objects.get(id=asignacion_id)
        data = json.loads(request.body)
        
        nuevo_estado = data.get('activo', True)
        
        # Actualizar el estado
        asignacion.activo = nuevo_estado
        asignacion.save()
        
        estado_texto = 'activada' if nuevo_estado else 'desactivada'
        
        return JsonResponse({
            'success': True, 
            'message': f'Asignación {estado_texto} exitosamente.',
            'asignacion': {
                'id': asignacion.id,
                'activo': asignacion.activo
            }
        })
        
    except UsuarioNivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Asignación no encontrada.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_eliminar_asignacion_comite(request, asignacion_id):
    """
    API para eliminar una asignación de usuario al comité
    """
    try:
        # Solo superusuarios pueden eliminar asignaciones
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar asignaciones del comité.'}, status=403)
        
        asignacion = UsuarioNivelComite.objects.get(id=asignacion_id)
        
        usuario_nombre = asignacion.usuario.username
        nivel_nombre = asignacion.nivel.nombre
        
        # Verificar si el usuario tiene participaciones pendientes
        participaciones_pendientes = ParticipacionComite.objects.filter(
            usuario=asignacion.usuario,
            nivel=asignacion.nivel,
            resultado='PENDIENTE'
        ).count()
        
        if participaciones_pendientes > 0:
            return JsonResponse({
                'success': False, 
                'error': f'No se puede eliminar la asignación porque el usuario tiene {participaciones_pendientes} participación(es) pendiente(s) en el comité.'
            }, status=400)
        
        # Eliminar la asignación
        asignacion.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Asignación de "{usuario_nombre}" al nivel "{nivel_nombre}" eliminada exitosamente.'
        })
        
    except UsuarioNivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Asignación no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_estadisticas_comite(request):
    """
    API para obtener estadísticas del comité
    """
    try:
        # Solo superusuarios pueden ver estadísticas completas
        if not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para ver estadísticas del comité.'}, status=403)
        
        # Calcular estadísticas
        total_niveles = NivelComite.objects.count()
        usuarios_asignados = UsuarioNivelComite.objects.count()
        usuarios_activos = UsuarioNivelComite.objects.filter(activo=True).count()
        
        # Obtener el nivel más alto (menor orden)
        nivel_mas_alto = NivelComite.objects.order_by('orden').first()
        nivel_mas_alto_nombre = nivel_mas_alto.nombre if nivel_mas_alto else None
        
        estadisticas = {
            'total_niveles': total_niveles,
            'usuarios_asignados': usuarios_asignados,
            'usuarios_activos': usuarios_activos,
            'nivel_mas_alto': nivel_mas_alto_nombre
        }
        
        return JsonResponse({'success': True, 'estadisticas': estadisticas})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500) 