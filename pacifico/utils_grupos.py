"""
Utilidades para gestión de grupos y supervisión
"""
from django.contrib.auth.models import User, Group
from .models import GroupProfile


def obtener_grupos_supervisados_por_usuario(usuario):
    """
    Retorna todos los grupos que el usuario supervisa
    """
    try:
        return GroupProfile.objects.filter(supervisores=usuario)
    except:
        return GroupProfile.objects.none()


def obtener_usuarios_supervisados_por_usuario(usuario):
    """
    Retorna todos los usuarios que están en grupos supervisados por el usuario dado
    """
    grupos_supervisados = obtener_grupos_supervisados_por_usuario(usuario)
    
    # En lugar de usar union(), vamos a usar una lista de IDs y luego hacer un filter
    usuarios_supervisados_ids = set()
    
    for grupo_profile in grupos_supervisados:
        # Obtener miembros del grupo
        miembros = grupo_profile.group.user_set.all()
        usuarios_supervisados_ids.update(miembros.values_list('id', flat=True))
    
    # Retornar queryset con los IDs únicos
    if usuarios_supervisados_ids:
        return User.objects.filter(id__in=usuarios_supervisados_ids)
    else:
        return User.objects.none()


def puede_ver_solicitudes_de_grupo(usuario, grupo):
    """
    Verifica si un usuario puede ver las solicitudes de un grupo específico
    """
    # Si es miembro del grupo
    if grupo.user_set.filter(id=usuario.id).exists():
        return True
    
    # Si es supervisor del grupo
    try:
        grupo_profile = grupo.profile
        if grupo_profile.puede_supervisar(usuario):
            return True
    except GroupProfile.DoesNotExist:
        pass
    
    # Si es administrador
    try:
        if usuario.userprofile.rol == 'Administrador':
            return True
    except:
        pass
    
    return False


def obtener_solicitudes_visibles_para_usuario(usuario, modelo_solicitud):
    """
    Retorna las solicitudes que un usuario puede ver basado en:
    1. Sus propias solicitudes
    2. Solicitudes de usuarios en grupos que supervisa
    3. Si es administrador, todas las solicitudes
    
    Args:
        usuario: El usuario para quien filtrar
        modelo_solicitud: El modelo de solicitud (ej: Cotizacion)
    """
    try:
        user_profile = usuario.userprofile
        
        # Si es administrador, puede ver todo
        if user_profile.rol == 'Administrador':
            return modelo_solicitud.objects.all()
        
        # Obtener solicitudes propias
        solicitudes_propias = modelo_solicitud.objects.filter(
            # Asumir que hay un campo 'usuario' o 'creado_por' en el modelo
            # Ajustar según el campo real en tu modelo
            usuario=usuario
        )
        
        # Si es supervisor, agregar solicitudes de usuarios supervisados
        if user_profile.rol in ['Supervisor', 'Asistente']:
            usuarios_supervisados = obtener_usuarios_supervisados_por_usuario(usuario)
            if usuarios_supervisados.exists():
                # Usar Q objects en lugar de union() para evitar problemas de columnas
                from django.db.models import Q
                solicitudes_supervisadas = modelo_solicitud.objects.filter(
                    Q(usuario__in=usuarios_supervisados)
                )
                
                # Combinar usando Q objects en lugar de union()
                return modelo_solicitud.objects.filter(
                    Q(usuario=usuario) | Q(usuario__in=usuarios_supervisados)
                )
        
        # Para otros roles, solo sus propias solicitudes
        return solicitudes_propias
        
    except Exception as e:
        # En caso de error, retornar solo solicitudes propias como fallback
        return modelo_solicitud.objects.filter(usuario=usuario)


def asignar_supervisor_a_grupo(grupo_nombre, supervisor_username):
    """
    Función helper para asignar un supervisor a un grupo
    """
    try:
        grupo = Group.objects.get(name=grupo_nombre)
        supervisor = User.objects.get(username=supervisor_username)
        
        # Verificar que el usuario tenga rol de supervisor o administrador
        if hasattr(supervisor, 'userprofile'):
            if supervisor.userprofile.rol in ['Supervisor', 'Administrador']:
                grupo_profile, created = GroupProfile.objects.get_or_create(group=grupo)
                grupo_profile.supervisores.add(supervisor)
                return True, f"Supervisor {supervisor_username} asignado al grupo {grupo_nombre}"
            else:
                return False, f"El usuario {supervisor_username} no tiene rol de Supervisor o Administrador"
        else:
            return False, f"El usuario {supervisor_username} no tiene UserProfile"
            
    except Group.DoesNotExist:
        return False, f"Grupo {grupo_nombre} no encontrado"
    except User.DoesNotExist:
        return False, f"Usuario {supervisor_username} no encontrado"
    except Exception as e:
        return False, f"Error: {str(e)}"


def es_supervisor_efectivo(usuario):
    """
    Determina si un usuario puede actuar como supervisor, ya sea por:
    1. Rol de Supervisor o Administrador
    2. Ser supervisor asignado de algún grupo
    """
    try:
        # Verificar por rol
        if hasattr(usuario, 'userprofile'):
            if usuario.userprofile.rol in ['Supervisor', 'Administrador']:
                return True
        
        # Verificar si es supervisor de algún grupo
        grupos_supervisados = obtener_grupos_supervisados_por_usuario(usuario)
        return grupos_supervisados.exists()
        
    except Exception:
        return False


def obtener_todos_los_datos_visibles_para_usuario(usuario, modelo):
    """
    Retorna todos los datos que un usuario puede ver basado en:
    1. Sus propios datos
    2. Datos de usuarios en grupos que supervisa
    3. Si es administrador, todos los datos
    """
    try:
        user_profile = usuario.userprofile
        
        # Si es administrador, puede ver todo
        if user_profile.rol == 'Administrador':
            return modelo.objects.all()
        
        # Obtener datos propios
        datos_propios = modelo.objects.filter(propietario=usuario)
        
        # Si es supervisor efectivo, agregar datos supervisados
        if es_supervisor_efectivo(usuario):
            usuarios_supervisados = obtener_usuarios_supervisados_por_usuario(usuario)
            if usuarios_supervisados.exists():
                # Usar Q objects en lugar de union() para evitar problemas de columnas
                from django.db.models import Q
                return modelo.objects.filter(
                    Q(propietario=usuario) | Q(propietario__in=usuarios_supervisados)
                )
        
        # Para otros casos, solo sus propios datos
        return datos_propios
        
    except Exception:
        # En caso de error, retornar solo datos propios como fallback
        return modelo.objects.filter(propietario=usuario)


def obtener_estadisticas_supervision(usuario):
    """
    Retorna estadísticas de supervisión para un usuario
    """
    grupos_supervisados = obtener_grupos_supervisados_por_usuario(usuario)
    usuarios_supervisados = obtener_usuarios_supervisados_por_usuario(usuario)
    
    return {
        'grupos_supervisados': grupos_supervisados.count(),
        'usuarios_supervisados': usuarios_supervisados.count(),
        'grupos_supervisados_list': [gp.group.name for gp in grupos_supervisados],
        'usuarios_supervisados_list': [u.username for u in usuarios_supervisados],
        'es_supervisor_efectivo': es_supervisor_efectivo(usuario)
    }
