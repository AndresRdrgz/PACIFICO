from django import forms
from .models import Cliente, UserProfile
from django.contrib.auth.models import User

# Base form with common widget styling
class BaseClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        
        widgets = {
            'cedulaCliente': forms.TextInput(attrs={
                'placeholder': 'Cédula del Cliente',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'nombreCliente': forms.TextInput(attrs={
                'placeholder': 'Nombre del Cliente',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'fechaNacimiento': forms.DateInput(attrs={
                'placeholder': 'Fecha de Nacimiento',
                'class': 'w-full text-slate-600 text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:border-blue-500',
                'type': 'date',
            }),
            'edad': forms.NumberInput(attrs={
                'placeholder': 'Edad',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'sexo': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'jubilado': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'propietario': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
        }
    
    def configure_propietario_field(self, user):
        if 'propietario' in self.fields:
            allowed_roles = ['Oficial', 'Administrador', 'Supervisor']
            users_with_allowed_roles = User.objects.filter(
                userprofile__rol__in=allowed_roles
            ).distinct().order_by('first_name', 'last_name', 'username')
            # Fallback: if no users with allowed roles, show all users
            if not users_with_allowed_roles.exists():
                users_with_allowed_roles = User.objects.all().order_by('first_name', 'last_name', 'username')
            self.fields['propietario'] = forms.ModelChoiceField(
                queryset=users_with_allowed_roles,
                label='Propietario',
                widget=forms.Select(attrs={
                    'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                })
            )
            
            # Set current user as default propietario if available and has allowed role
            if user and user.is_authenticated:
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.rol in allowed_roles:
                        self.fields['propietario'].initial = user.pk
                except UserProfile.DoesNotExist:
                    pass

# Cliente form for creating a new client (minimal fields)
class ClienteForm(BaseClienteForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show specific fields for the create form
        field_list = ['cedulaCliente', 'nombreCliente', 'propietario']
        for field_name in list(self.fields.keys()):
            if field_name not in field_list:
                self.fields.pop(field_name)
        
        # Configure the propietario field with allowed roles
        self.configure_propietario_field(user)
        
        # Configure nombreCliente field
        if 'nombreCliente' in self.fields:
            self.fields['nombreCliente'].widget.attrs.update({
                'autofocus': 'autofocus',
                'placeholder': 'Ingrese el nombre completo del cliente'
            })
            
        # Configure cedulaCliente field  
        if 'cedulaCliente' in self.fields:
            self.fields['cedulaCliente'].widget.attrs.update({
                'placeholder': 'Ingrese la cédula del cliente'
            })

# Cliente form for editing (all fields)
class EditClienteForm(BaseClienteForm):
    class Meta(BaseClienteForm.Meta):
        fields = ['nombreCliente', 'cedulaCliente', 'fechaNacimiento', 'edad', 'sexo', 'jubilado', 'propietario']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configure the propietario field with allowed roles
        self.configure_propietario_field(user)
        
        # Add additional styling and hints to fields
        if 'fechaNacimiento' in self.fields:
            self.fields['fechaNacimiento'].widget.attrs.update({
                'onchange': 'updateAge(this.value)'
            })
            
        if 'edad' in self.fields:
            self.fields['edad'].widget.attrs.update({
                'readonly': 'readonly',
                'placeholder': 'Calculado automáticamente'
            })