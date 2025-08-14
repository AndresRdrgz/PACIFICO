"""
Utilidades para gestión de cotizaciones con supervisión de grupo
"""
from django.db.models import QuerySet
from .models import Cotizacion


def obtener_cotizaciones_para_usuario(usuario, queryset=None, limit=None):
    """
    Retorna las cotizaciones que un usuario puede ver:
    1. Sus propias cotizaciones
    2. Cotizaciones de usuarios que supervisa (si es supervisor de grupo)
    
    Args:
        usuario: Usuario autenticado
        queryset: QuerySet base de cotizaciones (opcional)
        limit: Límite de resultados (opcional)
    
    Returns:
        QuerySet de cotizaciones
    """
    if not usuario.is_authenticated:
        return Cotizacion.objects.none()
    
    # Si es staff/superuser, ver todas
    if usuario.is_staff:
        if queryset is not None:
            return queryset
        return Cotizacion.objects.all()
    
    # Usuario normal: ver sus propias cotizaciones
    if queryset is not None:
        cotizaciones_propias = queryset.filter(added_by=usuario)
    else:
        cotizaciones_propias = Cotizacion.objects.filter(added_by=usuario)
    
    # Verificar si es supervisor de grupo
    usuarios_supervisados = []
    try:
        from .utils_grupos import obtener_grupos_supervisados_por_usuario
        grupos_supervisados = obtener_grupos_supervisados_por_usuario(usuario)
        
        if grupos_supervisados.exists():
            # Obtener usuarios supervisados
            for grupo_profile in grupos_supervisados:
                miembros = grupo_profile.group.user_set.all()
                usuarios_supervisados.extend(miembros)
    except ImportError:
        pass  # Si no existe el módulo, continuar sin supervisión
    
    # Combinar cotizaciones propias + supervisadas usando Q objects
    from django.db.models import Q
    
    if usuarios_supervisados:
        # Usar Q objects para combinar filtros en lugar de union()
        if queryset is not None:
            # Si tenemos un queryset base, aplicar filtros combinados
            cotizaciones = queryset.filter(
                Q(added_by=usuario) | Q(added_by__in=usuarios_supervisados)
            )
        else:
            # Si no hay queryset base, crear uno nuevo
            cotizaciones = Cotizacion.objects.filter(
                Q(added_by=usuario) | Q(added_by__in=usuarios_supervisados)
            )
    else:
        cotizaciones = cotizaciones_propias
    
    # Aplicar límite si se especifica
    if limit is not None:
        cotizaciones = cotizaciones[:limit]
    
    return cotizaciones


def obtener_cotizaciones_para_usuario_con_orden(usuario, orden='-created_at', limit=None):
    """
    Retorna las cotizaciones ordenadas que un usuario puede ver
    
    Args:
        usuario: Usuario autenticado
        orden: Campo de ordenamiento (default: '-created_at')
        limit: Límite de resultados (opcional)
    
    Returns:
        QuerySet de cotizaciones ordenadas
    """
    cotizaciones = obtener_cotizaciones_para_usuario(usuario, limit=limit)
    
    # Aplicar ordenamiento
    if orden:
        cotizaciones = cotizaciones.order_by(orden)
    
    # Aplicar límite después del ordenamiento
    if limit is not None:
        cotizaciones = cotizaciones[:limit]
    
    return cotizaciones


def es_supervisor_cotizaciones(usuario):
    """
    Verifica si un usuario es supervisor de cotizaciones
    
    Args:
        usuario: Usuario a verificar
    
    Returns:
        bool: True si es supervisor, False en caso contrario
    """
    if not usuario.is_authenticated:
        return False
    
    if usuario.is_staff:
        return True
    
    try:
        from .utils_grupos import obtener_grupos_supervisados_por_usuario
        grupos_supervisados = obtener_grupos_supervisados_por_usuario(usuario)
        return grupos_supervisados.exists()
    except ImportError:
        return False

