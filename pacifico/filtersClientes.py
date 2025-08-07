import django_filters
from django import forms
from django.contrib.auth.models import User
from .models import Cliente, UserProfile

class ClienteFilter(django_filters.FilterSet):
    propietario = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.filter(
            is_active=True,
            userprofile__rol__in=['Oficial', 'Asistente', 'Supervisor', 'Administrador']
        ).order_by('first_name', 'last_name', 'username'),
        label='Propietario',
        widget=forms.SelectMultiple(attrs={
            'class': 'hidden',  # We'll hide the default widget and use our custom one
            'id': 'propietario-select'
        })
    )

    class Meta:
        model = Cliente
        fields = ['propietario']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Verificar si el usuario puede usar el filtro
        puede_usar_filtro = False
        
        if user:
            # Administradores y superusuarios siempre pueden usar el filtro
            if user.is_superuser:
                puede_usar_filtro = True
            else:
                # Verificar rol de usuario o si es supervisor efectivo
                try:
                    user_rol = user.userprofile.rol
                    if user_rol in ['Supervisor', 'Administrador']:
                        puede_usar_filtro = True
                    else:
                        # Verificar si es supervisor de algún grupo
                        from .utils_grupos import es_supervisor_efectivo
                        puede_usar_filtro = es_supervisor_efectivo(user)
                except:
                    pass
        
        # Solo mostrar el filtro si el usuario tiene permisos
        if not puede_usar_filtro:
            self.filters.clear()
