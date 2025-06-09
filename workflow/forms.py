from django import forms
from .models import ClienteEntrevista

class ClienteEntrevistaForm(forms.ModelForm):
    class Meta:
        model = ClienteEntrevista
        fields = ['nombre', 'cedula', 'fecha_nacimiento', 'telefono', 'email', 'direccion', 'ocupacion', 'empresa', 'salario']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre completo',
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Cédula',
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Teléfono',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Correo electrónico',
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Dirección',
            }),
            'ocupacion': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ocupación',
            }),
            'empresa': forms.TextInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Empresa',
            }),
            'salario': forms.NumberInput(attrs={
                'class': 'w-full bg-white border border-gray-300 rounded-md px-3 py-2 mb-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Salario',
                'step': '0.01',
            }),
        }
