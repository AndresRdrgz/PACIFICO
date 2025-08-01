from django.contrib.auth.models import Group
from .models import Etapa, PermisoBandeja

def user_navigation_permissions(request):
    """
    Context processor para proporcionar permisos de navegación del usuario.
    """
    context = {
        'can_access_comite': False,
        'can_access_bandejas_trabajo': False,
        'can_access_canal_digital': False,
        'can_access_pendientes_errores': False,
    }
    
    if not request.user.is_authenticated:
        return context
    
    # Superusuarios pueden acceder a todo
    if request.user.is_superuser:
        context.update({
            'can_access_comite': True,
            'can_access_bandejas_trabajo': True,
            'can_access_canal_digital': True,
            'can_access_pendientes_errores': True,
        })
        return context
    
    # Verificar acceso al Comité de Crédito
    try:
        if request.user.groups.filter(name="Comité de Crédito").exists():
            context['can_access_comite'] = True
    except:
        pass
    
    # Verificar acceso a Bandejas de Trabajo (si tiene acceso a alguna etapa de bandeja grupal)
    try:
        # Obtener todas las etapas que son bandejas grupales
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True)
        
        # Verificar si el usuario tiene permisos en alguna de estas etapas
        user_groups = request.user.groups.all()
        
        for etapa in etapas_grupales:
            # Verificar permisos por grupo
            if PermisoBandeja.objects.filter(
                etapa=etapa,
                grupo__in=user_groups,
                puede_ver=True
            ).exists():
                context['can_access_bandejas_trabajo'] = True
                break
            
            # Verificar permisos directos por usuario
            if PermisoBandeja.objects.filter(
                etapa=etapa,
                usuario=request.user,
                puede_ver=True
            ).exists():
                context['can_access_bandejas_trabajo'] = True
                break
    except:
        pass
    
    # Verificar acceso al Canal Digital
    try:
        if request.user.groups.filter(name="Canal Digital").exists():
            context['can_access_canal_digital'] = True
    except:
        pass
    
    # Verificar acceso a Pendientes y Errores
    try:
        if request.user.groups.filter(name__in=["NEGOCIOS", "BACK OFFICE"]).exists():
            context['can_access_pendientes_errores'] = True
    except:
        pass
    
    return context
