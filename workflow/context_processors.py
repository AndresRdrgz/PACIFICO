from django.contrib.auth.models import Group
from .models import Etapa, PermisoBandeja, PermisoPipeline
from pacifico.models import UserProfile

def user_navigation_permissions(request):
    """
    Context processor para proporcionar permisos de navegación del usuario basado en roles.
    """
    context = {
        'can_access_comite': False,
        'can_access_bandejas_trabajo': False,
        'can_access_canal_digital': False,
        'can_access_pendientes_errores': False,
        'can_access_negocios': False,
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
            'can_access_negocios': True,
        })
        return context
    
    # Obtener el rol del usuario
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_role = user_profile.rol
    except UserProfile.DoesNotExist:
        user_role = None
    
    # Verificar acceso basado en rol y permisos configurados
    
    # Acceso a Negocios: Oficial de Negocio, Asistente, Supervisor, Administrador
    if user_role in ['Oficial', 'Asistente', 'Supervisor', 'Administrador']:
        context['can_access_negocios'] = True
    
    # Acceso a Comité: Roles que pueden participar en comité + usuarios con permisos específicos
    if user_role in ['Supervisor', 'Administrador']:
        context['can_access_comite'] = True
    
    # Acceso a Bandejas de Trabajo: Analistas y Back Office siempre pueden ver, otros según permisos
    if user_role in ['Analista', 'Back Office']:
        context['can_access_bandejas_trabajo'] = True
    else:
        try:
            # Verificar permisos directos por usuario
            if PermisoBandeja.objects.filter(
                usuario=request.user,
                puede_ver=True
            ).exists():
                context['can_access_bandejas_trabajo'] = True
            
            # Verificar permisos por grupos (si los tiene)
            user_groups = request.user.groups.all()
            if user_groups.exists() and PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                puede_ver=True
            ).exists():
                context['can_access_bandejas_trabajo'] = True
        except:
            pass
    
    # Acceso al Canal Digital: Verificar grupo específico
    try:
        if request.user.groups.filter(name="Canal Digital").exists():
            context['can_access_canal_digital'] = True
    except:
        pass
    
    # Acceso a Pendientes y Errores: Roles administrativos
    if user_role in ['Supervisor', 'Administrador']:
        context['can_access_pendientes_errores'] = True
    
    return context
