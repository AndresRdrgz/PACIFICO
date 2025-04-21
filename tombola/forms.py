from django import forms
from .models import FormularioTombola, Tombola, Boleto

class FormularioTombolaForm(forms.ModelForm):
    class Meta:
        model = FormularioTombola
        fields = [
            'nombre',
            'apellido',
            'cedulaCliente',
            'celular',
            'correo_electronico',
            'edad',
            'fecha_nacimiento',
            'sexo',
            'sector',
            'salario',
            'producto_interesado',
            'dinero_a_solicitar',
            'oficial',
            'autorizacion_apc',
            'acepta_condiciones',
            'tombola',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'apellido': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'cedulaCliente': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'celular': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'edad': forms.NumberInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'sexo': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'sector': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'salario': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'type': 'date'}),
            'producto_interesado': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'dinero_a_solicitar': forms.NumberInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'oficial': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'autorizacion_apc': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
            'acepta_condiciones': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
            'tombola': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['nombre'].required = True
        self.fields['apellido'].required = True
        self.fields['cedulaCliente'].required = True
        self.fields['tombola'].required = True
        self.fields['fecha_nacimiento'].required = True
        self.fields['edad'].required = False

        # Set other fields as not required
        for field_name in self.fields:
            if field_name not in ['nombre', 'apellido', 'cedulaCliente', 'tombola']:
                self.fields[field_name].required = False

            # Add error class if the field has errors after form validation
            if hasattr(self, 'errors'):
                for field_name in self.errors:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f"{existing_classes} border-red-500"