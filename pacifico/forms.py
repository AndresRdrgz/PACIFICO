import os
from django import forms
from .models import Cotizacion, Aseguradora, Cliente, UserProfile
from django.contrib.auth.models import User
from pathlib import Path
import json
from django.conf import settings

# Load the JSON file
BASE_DIR = Path(__file__).resolve().parent.parent
with open(BASE_DIR / 'static/insumos/autos.json') as f:
    choices_data = json.load(f)

# Extract unique values for the "MARCA" field
unique_marcas = list({item['MARCA'] for item in choices_data})

# Convert unique "MARCA" values to choices format and add a default choice
marca_choices = [('', 'Seleccione una marca')] + [(marca, marca) for marca in unique_marcas]

#FORMAULRIOS AQUI

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['sucursal', 'oficial']
        widgets = {
            'sucursal': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'oficial': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Nombre',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Apellido',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Correo Electrónico',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
        }

class AseguradoraForm(forms.ModelForm):

    class Meta:
        model = Aseguradora
        fields = '__all__'

#Cliente form all fields
class ClienteForm(forms.ModelForm):
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
            'patrono': forms.TextInput(attrs={
                'placeholder': 'Patrono',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
        }
class FideicomisoForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = '__all__'
        
        widgets = {
            'added_by': forms.HiddenInput(),
            'nombreCliente': forms.TextInput(attrs={
                'placeholder': 'Nombre del Cliente',      
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'cedulaCliente': forms.TextInput(attrs={
                'placeholder': 'Cédula del Cliente',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'tipoDocumento': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',

            }),

            'fechaNacimiento': forms.DateInput(attrs={
                'placeholder': 'Fecha de Inicio',
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
            'apcScore': forms.NumberInput(attrs={
                'placeholder': 'APC Score',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'apcPI': forms.NumberInput(attrs={
                'placeholder': 'APC PI',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'fechaInicioPago': forms.DateInput(attrs={
                'placeholder': 'Fecha de Inicio',
                'class': 'w-full text-slate-600 text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:border-blue-500',
                'type': 'date',
                'readonly': 'readonly',
            }),
            'comiCierre': forms.NumberInput(attrs={
                'placeholder': 'Comisión de Cierre',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'plazoPago': forms.NumberInput(attrs={
                'placeholder': 'Plazo de Pago',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'tasaEstimada': forms.NumberInput(attrs={
                'placeholder': 'Tasa Estimada',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
         

            'montoPrestamo': forms.NumberInput(attrs={
                'placeholder': 'Monto del Préstamo',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'readonly': 'readonly',
            }),
            'r_deseada': forms.NumberInput(attrs={
                'placeholder': 'R Deseada',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'tasaInteres': forms.NumberInput(attrs={
                'placeholder': 'Tasa de Interés',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'patrono': forms.TextInput(attrs={
                'placeholder': 'Patrono',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            
            }),
            'patronoCodigo': forms.NumberInput(attrs={
                'placeholder': 'Código del Patrono',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'vendedor': forms.TextInput(attrs={
                'placeholder': 'Vendedor',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                #'initial': '1 - SIN VENDEDOR',
                
                
            }),
            'vendedorComision': forms.NumberInput(attrs={
                'placeholder': 'Comisión del Vendedor',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'financiaSeguro': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600',
            }),
            'mesesFinanciaSeguro': forms.NumberInput(attrs={
                'placeholder': 'Meses de Financiamiento',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'required': False,
            }),
            'montoanualSeguro': forms.NumberInput(attrs={
                'placeholder': 'Monto Anual del Seguro',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'required': False,
            }),
            'montoMensualSeguro': forms.NumberInput(attrs={
                'placeholder': 'Monto Mensual del Seguro',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
                'required': False,
            }),
            'cantPagosSeguro': forms.NumberInput(attrs={
                'placeholder': 'Cantidad de Pagos del Seguro',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'required': False,
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'placeholder': 'Ingrese sus observaciones aquí',
                'rows': 4,  # Adjusts the default height of the textarea
            }),
            'tiempoServicio': forms.TextInput(attrs={
                'placeholder': 'Tiempo de Servicio',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'ingresos': forms.NumberInput(attrs={
                'placeholder': 'Ingresos',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            
            }),
            'nombreEmpresa': forms.TextInput(attrs={
                'placeholder': 'Nombre de la Empresa',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'referenciasAPC': forms.Select(attrs={
                'placeholder': 'Referencias APC',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
                
            'cartera': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'placeholder': 'Cartera',
            }),
           
            'licencia': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'posicion': forms.TextInput(attrs={
                'placeholder': 'Posición',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'perfilUniversitario': forms.TextInput(attrs={
                'placeholder': 'Perfil Universitario',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'oficial': forms.Select(attrs={
                'placeholder': 'Oficial',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'sucursal': forms.Select(attrs={
                'placeholder': 'Sucursal',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'cashback': forms.NumberInput(attrs={
                'placeholder': 'Cashback',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'abono': forms.NumberInput(attrs={
                'placeholder': 'Abono',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
              'abonoPorcentaje': forms.NumberInput(attrs={
                'placeholder': 'Abono',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            #NIVEL DE ENDEUDAMIENTO
            'salarioBaseMensual': forms.NumberInput(attrs={
                'placeholder': 'Salario Base Mensual',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'horasExtrasMonto': forms.NumberInput(attrs={
                'placeholder': 'Horas Extras Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'horasExtrasDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'primaMonto': forms.NumberInput(attrs={
                'placeholder': 'Prima Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'primaDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'bonosMonto': forms.NumberInput(attrs={
                'placeholder': 'Bonos Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'bonosDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'otrosMonto': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'otrosDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'siacapMonto'   : forms.NumberInput(attrs={
                'placeholder': 'SIACAP Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',

            }),
            'siacapDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'praaMonto': forms.NumberInput(attrs={
                'placeholder': 'PRAA Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'praaDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'dirOtros1': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosMonto1': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosDcto1': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'dirOtros2': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosMonto2': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosDcto2': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'dirOtros3': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosMonto3': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosDcto3': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'dirOtros4': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosMonto4': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'dirOtrosDcto4': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'pagoVoluntario1': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioMonto1': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioDcto1': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'pagoVoluntario2': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioMonto2': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioDcto2': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'pagoVoluntario3': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioMonto3': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioDcto3': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'pagoVoluntario4': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioMonto4': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioDcto4': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'pagoVoluntario5': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioMonto5': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioDcto5': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'pagoVoluntario6': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioMonto6': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'pagoVoluntarioDcto6': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'totalIngresosAdicionales': forms.NumberInput(attrs={
                'placeholder': 'Total Ingresos Adicionales',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            #DATOS DEL AUTO
            'valorAuto': forms.NumberInput(attrs={
                'placeholder': 'Valor del Auto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'marca':forms.TextInput(attrs={
                'placeholder': 'Marca del Auto',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'modelo':forms.TextInput(attrs={
                'placeholder': 'Modelo del Auto',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'yearCarro': forms.NumberInput(attrs={
                'placeholder': 'Año del Vehículo',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'yearsFinanciamiento': forms.NumberInput(attrs={
                'placeholder': 'Años de Financiamiento',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'transmisionAuto': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'kilometrajeAuto': forms.NumberInput(attrs={
                'placeholder': 'Kilometraje del Auto',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'nuevoAuto': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            



            #PRORRATEO
            'mes0': forms.NumberInput(attrs={
                'placeholder': 'Mes 1',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes1': forms.NumberInput(attrs={
                'placeholder': 'Mes 2',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes2': forms.NumberInput(attrs={
                'placeholder': 'Mes 3',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes3': forms.NumberInput(attrs={
                'placeholder': 'Mes 4',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes4': forms.NumberInput(attrs={
                'placeholder': 'Mes 5',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes5': forms.NumberInput(attrs={
                'placeholder': 'Mes 6',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes6': forms.NumberInput(attrs={
                'placeholder': 'Mes 7',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes7': forms.NumberInput(attrs={
                'placeholder': 'Mes 8',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes8': forms.NumberInput(attrs={
                'placeholder': 'Mes 9',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes9': forms.NumberInput(attrs={
                'placeholder': 'Mes 10',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes10': forms.NumberInput(attrs={
                'placeholder': 'Mes 11',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'mes11': forms.NumberInput(attrs={
                'placeholder': 'Mes 12',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'primerMes': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'tipoProrrateo': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            #CODEUDOR
            'aplicaCodeudor:': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorNombre': forms.TextInput(attrs={
                'placeholder': 'Nombre del Codeudor',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorCedula': forms.TextInput(attrs={
                'placeholder': 'Cédula del Codeudor',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',

            }),
            'codeudorEstabilidad': forms.TextInput(attrs={
                'placeholder': 'Estabilidad',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorIngresos': forms.NumberInput(attrs={
                'placeholder': 'Ingresos',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
             'codeudorCartera': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'placeholder': 'Cartera',
            }),
             'codeudorPosicion': forms.TextInput(attrs={
                'placeholder': 'Nombre del Codeudor',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorLicencia': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorEmpresa': forms.TextInput(attrs={
                'placeholder': 'Nombre de la Empresa',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorReferenciasAPC': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorNombreEmpres1': forms.TextInput(attrs={
                'placeholder': 'Nombre de la Empresa',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorPeriodo1': forms.TextInput(attrs={
                'placeholder': 'Periodo',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorSalario1': forms.NumberInput(attrs={
                'placeholder': 'Salario',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorNombreEmpres2': forms.TextInput(attrs={
                'placeholder': 'Nombre de la Empresa',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorPeriodo2': forms.TextInput(attrs={
                'placeholder': 'Periodo',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorSalario2': forms.NumberInput(attrs={
                'placeholder': 'Salario',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorNombreEmpres3': forms.TextInput(attrs={
                'placeholder': 'Nombre de la Empresa',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorPeriodo3': forms.TextInput(attrs={
                'placeholder': 'Periodo',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'codeudorSalario3': forms.NumberInput(attrs={
                'placeholder': 'Salario',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            #NIVEL DE ENDEUDAMIENTO - familiar
            'cosalarioBaseMensual': forms.NumberInput(attrs={
                'placeholder': 'Salario Base Mensual',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'cohorasExtrasMonto': forms.NumberInput(attrs={
                'placeholder': 'Horas Extras Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'cohorasExtrasDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'coprimaMonto': forms.NumberInput(attrs={
                'placeholder': 'Prima Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'coprimaDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'cobonosMonto': forms.NumberInput(attrs={
                'placeholder': 'Bonos Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'cobonosDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'cootrosMonto': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'cootrosDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'cosiacapMonto'   : forms.NumberInput(attrs={
                'placeholder': 'SIACAP Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',

            }),
            'cosiacapDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copraaMonto': forms.NumberInput(attrs={
                'placeholder': 'PRAA Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copraaDcto': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'codirOtros1': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosMonto1': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosDcto1': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'codirOtros2': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosMonto2': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosDcto2': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'codirOtros3': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosMonto3': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosDcto3': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'codirOtros4': forms.TextInput(attrs={
                'placeholder': 'Otros',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosMonto4': forms.NumberInput(attrs={
                'placeholder': 'Otros Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'codirOtrosDcto4': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copagoVoluntario1': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioMonto1': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioDcto1': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copagoVoluntario2': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioMonto2': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioDcto2': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copagoVoluntario3': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioMonto3': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioDcto3': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copagoVoluntario4': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioMonto4': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioDcto4': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copagoVoluntario5': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioMonto5': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioDcto5': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'copagoVoluntario6': forms.TextInput(attrs={
                'placeholder': 'Descripción',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioMonto6': forms.NumberInput(attrs={
                'placeholder': 'Pago Voluntario Monto',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            }),
            'copagoVoluntarioDcto6': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
            }),
            'cototalIngresosAdicionales': forms.NumberInput(attrs={
                'placeholder': 'Total Ingresos Adicionales',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            'cototalIngresosAdicionales': forms.NumberInput(attrs={
                'placeholder': 'Total Ingresos Adicionales',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            #movimientos
            'movPrimerMes': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'averageIngresos': forms.NumberInput(attrs={
                'placeholder': 'Average Ingresos',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'readonly': 'readonly',
            }),
            'ingresosMes1': forms.NumberInput(attrs={
                'placeholder': 'Mes 1',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'ingresosMes2': forms.NumberInput(attrs={
                'placeholder': 'Mes 2',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'ingresosMes3': forms.NumberInput(attrs={
                'placeholder': 'Mes 3',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'ingresosMes4': forms.NumberInput(attrs={
                'placeholder': 'Mes 4',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'ingresosMes5': forms.NumberInput(attrs={
                'placeholder': 'Mes 5',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'ingresosMes6': forms.NumberInput(attrs={
                'placeholder': 'Mes 6',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'egresosMes1': forms.NumberInput(attrs={
                'placeholder': 'Mes 1',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'egresosMes2': forms.NumberInput(attrs={
                'placeholder': 'Mes 2',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'egresosMes3': forms.NumberInput(attrs={
                'placeholder': 'Mes 3',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'egresosMes4': forms.NumberInput(attrs={
                'placeholder': 'Mes 4',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'egresosMes5': forms.NumberInput(attrs={
                'placeholder': 'Mes 5',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'egresosMes6': forms.NumberInput(attrs={
                'placeholder': 'Mes 6',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'step': '0.01',
                'oninput': 'validateDecimal(this)',
            }),
            'movOpcion': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            
        }

    periodoPago = forms.ChoiceField(
        choices=[(1, 'MENSUAL')],
        initial=1,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    formaPago = forms.ChoiceField(
        choices=[(1, '1 - PAGO VOLUNTARIO')],
        initial=1,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    aseguradora = forms.ModelChoiceField(
        queryset=Aseguradora.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    tasaBruta = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Tasa Bruta',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )

    aseguradoraAuto = forms.ChoiceField(
        choices=[(6, 'SEGUROS SURAMERICANA, S.A.')],
        initial=6,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )
    corredorSeguro = forms.ChoiceField(
        choices=[(3, 'ROLKAM Y ASOCIADOS, S.A.')],
        initial=3,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )
    tipoSeguro = forms.ChoiceField(
        choices=[('INCLUIDO', 'Incluido'), ('NO INCLUIDO', 'No Incluido')],
        initial='INCLUIDO',
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    frecuenciaPagoSeguro = forms.ChoiceField(
        choices=[('MENSUAL', 'MENSUAL')],
        initial='MENSUAL',
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )

    
    marcaAuto = forms.ChoiceField(
        choices=marca_choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    lineaAuto = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Línea del Vehículo',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    yearAuto = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Año del Vehículo',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )

    
    
    #ENDEUDAMIENTO
    
   
    #descuento directo
    
   
    
    #PAGOS VOLUNTARIOS
    pagoVoluntario1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioMonto1 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Pago Voluntario Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioDcto1 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    pagoVoluntario2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioMonto2 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Pago Voluntario Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioDcto2 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    pagoVoluntario3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioMonto3 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Pago Voluntario Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioDcto3 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    pagoVoluntario4 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioMonto4 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Pago Voluntario Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioDcto4 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    pagoVoluntario5 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioMonto5 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Pago Voluntario Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioDcto5 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    pagoVoluntario6 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Descripción',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioMonto6 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Pago Voluntario Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    pagoVoluntarioDcto6 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['nombreCliente'].required = False
        #self.fields['cedulaCliente'].required = False
        self.fields['tiempoServicio'].required = False
        self.fields['ingresos'].required = False
        self.fields['nombreEmpresa'].required = False
        self.fields['referenciasAPC'].required = False
        self.fields['licencia'].required = False
        self.fields['posicion'].required = False
        self.fields['perfilUniversitario'].required = False
        #self.fields['oficial'].required = False
        #self.fields['vendedor'].required = False
        self.fields['montoPrestamo'].required = False
        self.fields['fechaInicioPago'].required = False
        self.fields['salarioBaseMensual'].required = False
        self.fields['cashback'].required = False
        self.fields['abono'].required = False
        self.fields['abonoPorcentaje'].required = False
        self.fields['totalIngresosAdicionales'].required = False
        self.fields['cototalIngresosAdicionales'].required = False
        self.fields['yearsFinanciamiento'].required = False
        self.fields['tasaEstimada'].required = False
        self.fields['tasaBruta'].required = False
        self.fields['auxMonto2'].required = False
        self.fields['wrkMontoLetra'].required = False
        self.fields['wrkLetraSeguro'].required = False
        self.fields['wrkLetraSinSeguros'].required = False
        self.fields['montoMensualSeguro'].required = False
        self.fields['r1'].required = False
        self.fields['calcComiCierreFinal'].required = False
        self.fields['calcMontoNotaria'].required = False
        self.fields['calcMontoTimbres'].required = False
        self.fields['tablaTotalPagos'].required = False
        self.fields['tablaTotalSeguro'].required = False
        self.fields['tablaTotalFeci'].required = False
        self.fields['tablaTotalInteres'].required = False
        self.fields['tablaTotalMontoCapital'].required = False
        self.fields['manejo_5porc'].required = False
        self.fields['apcScore'].required = False
        self.fields['apcPI'].required = False
        self.fields['cartera'].required = False
        self.fields['siacapMonto'].required = False
        self.fields['siacapDcto'].required = False
        self.fields['praaMonto'].required = False
        self.fields['praaDcto'].required = False
        self.fields['dirOtros1'].required = False
        self.fields['dirOtrosMonto1'].required = False
        self.fields['dirOtrosDcto1'].required = False
        self.fields['dirOtros2'].required = False
        self.fields['dirOtrosMonto2'].required = False
        self.fields['dirOtrosDcto2'].required = False
        self.fields['dirOtros3'].required = False
        self.fields['dirOtrosMonto3'].required = False
        self.fields['dirOtrosDcto3'].required = False
        self.fields['dirOtros4'].required = False
        self.fields['dirOtrosMonto4'].required = False
        self.fields['dirOtrosDcto4'].required = False
        self.fields['pagoVoluntario1'].required = False
        self.fields['pagoVoluntarioMonto1'].required = False
        self.fields['pagoVoluntarioDcto1'].required = False
        self.fields['pagoVoluntario2'].required = False
        self.fields['pagoVoluntarioMonto2'].required = False
        self.fields['pagoVoluntarioDcto2'].required = False
        self.fields['pagoVoluntario3'].required = False
        self.fields['pagoVoluntarioMonto3'].required = False
        self.fields['pagoVoluntarioDcto3'].required = False
        self.fields['pagoVoluntario4'].required = False
        self.fields['pagoVoluntarioMonto4'].required = False
        self.fields['pagoVoluntarioDcto4'].required = False
        self.fields['pagoVoluntario5'].required = False
        self.fields['pagoVoluntarioMonto5'].required = False
        self.fields['pagoVoluntarioDcto5'].required = False
        self.fields['pagoVoluntario6'].required = False
        self.fields['pagoVoluntarioMonto6'].required = False
        self.fields['pagoVoluntarioDcto6'].required = False
        self.fields['totalDescuentosLegales'].required = False
        self.fields['totalDescuentoDirecto'].required = False
        self.fields['totalPagoVoluntario'].required = False
        self.fields['salarioNetoActual'].required = False
        self.fields['salarioNeto'].required = False
        self.fields['porSalarioNeto'].required = False
        self.fields['totalIngresosMensualesCompleto'].required = False
        self.fields['totalDescuentosLegalesCompleto'].required = False
        self.fields['salarioNetoActualCompleto'].required = False
        self.fields['salarioNetoCompleto'].required = False
        self.fields['porSalarioNetoCompleto'].required = False
        self.fields['horasExtrasMonto'].required = False
        self.fields['horasExtrasDcto'].required = False
        self.fields['primaMonto'].required = False
        self.fields['primaDcto'].required = False
        self.fields['bonosMonto'].required = False
        self.fields['bonosDcto'].required = False
        self.fields['otrosMonto'].required = False
        self.fields['otrosDcto'].required = False
        self.fields['mes0'].required = False
        self.fields['mes1'].required = False
        self.fields['mes2'].required = False
        self.fields['mes3'].required = False
        self.fields['mes4'].required = False
        self.fields['mes5'].required = False
        self.fields['mes6'].required = False
        self.fields['mes7'].required = False
        self.fields['mes8'].required = False
        self.fields['mes9'].required = False
        self.fields['mes10'].required = False
        self.fields['mes11'].required = False
        self.fields['primerMes'].required = False
        self.fields['tipoProrrateo'].required = False
        self.fields['marca'].required = False
        self.fields['modelo'].required = False
        self.fields['yearCarro'].required = False
        self.fields['patronoCodigo'].required = False
        self.fields['montoManejoT'].required = False
        self.fields['monto_manejo_b'].required = False
        self.fields['codeudorNombre'].required = False
        self.fields['codeudorCedula'].required = False
        self.fields['codeudorEstabilidad'].required = False
        self.fields['codeudorIngresos'].required = False
        self.fields['codeudorLicencia'].required = False
        self.fields['codeudorEmpresa'].required = False
        self.fields['codeudorReferenciasAPC'].required = False
        self.fields['codeudorNombreEmpres1'].required = False
        self.fields['codeudorPeriodo1'].required = False
        self.fields['codeudorSalario1'].required = False
        self.fields['codeudorNombreEmpres2'].required = False
        self.fields['codeudorPeriodo2'].required = False
        self.fields['codeudorSalario2'].required = False
        self.fields['codeudorNombreEmpres3'].required = False
        self.fields['codeudorPeriodo3'].required = False
        self.fields['codeudorSalario3'].required = False
        self.fields['aplicaCodeudor'].required = False
        #endeudamiento familiar
        self.fields['cosiacapMonto'].required = False
        self.fields['cosiacapDcto'].required = False
        self.fields['copraaMonto'].required = False
        self.fields['copraaDcto'].required = False
        self.fields['codirOtros1'].required = False
        self.fields['codirOtrosMonto1'].required = False
        self.fields['codirOtrosDcto1'].required = False
        self.fields['codirOtros2'].required = False
        self.fields['codirOtrosMonto2'].required = False
        self.fields['codirOtrosDcto2'].required = False
        self.fields['codirOtros3'].required = False
        self.fields['codirOtrosMonto3'].required = False
        self.fields['codirOtrosDcto3'].required = False
        self.fields['codirOtros4'].required = False
        self.fields['codirOtrosMonto4'].required = False
        self.fields['codirOtrosDcto4'].required = False
        self.fields['copagoVoluntario1'].required = False
        self.fields['copagoVoluntarioMonto1'].required = False
        self.fields['copagoVoluntarioDcto1'].required = False
        self.fields['copagoVoluntario2'].required = False
        self.fields['copagoVoluntarioMonto2'].required = False
        self.fields['copagoVoluntarioDcto2'].required = False
        self.fields['copagoVoluntario3'].required = False
        self.fields['copagoVoluntarioMonto3'].required = False
        self.fields['copagoVoluntarioDcto3'].required = False
        self.fields['copagoVoluntario4'].required = False
        self.fields['copagoVoluntarioMonto4'].required = False
        self.fields['copagoVoluntarioDcto4'].required = False
        self.fields['copagoVoluntario5'].required = False
        self.fields['copagoVoluntarioMonto5'].required = False
        self.fields['copagoVoluntarioDcto5'].required = False
        self.fields['copagoVoluntario6'].required = False
        self.fields['copagoVoluntarioMonto6'].required = False
        self.fields['copagoVoluntarioDcto6'].required = False
        self.fields['cohorasExtrasMonto'].required = False
        self.fields['cohorasExtrasDcto'].required = False
        self.fields['cohorasExtrasMonto'].required = False
        self.fields['coprimaMonto'].required = False
        self.fields['cobonosMonto'].required = False
        self.fields['cootrosMonto'].required = False
        self.fields['codeudorCartera'].required = False
        self.fields['codeudorPosicion'].required = False
        self.fields['cosalarioBaseMensual'].required = False
        self.fields['cototalDescuentosLegales'].required = False
        self.fields['cototalDescuentoDirecto'].required = False
        self.fields['cototalPagoVoluntario'].required = False
        self.fields['cosalarioNetoActual'].required = False
        self.fields['cosalarioNeto'].required = False
        self.fields['coporSalarioNeto'].required = False
        self.fields['cototalIngresosAdicionales'].required = False
        self.fields['cototalIngresosMensualesCompleto'].required = False
        self.fields['cototalDescuentosLegalesCompleto'].required = False
        self.fields['cosalarioNetoActualCompleto'].required = False
        self.fields['cosalarioNetoCompleto'].required = False
        self.fields['coporSalarioNetoCompleto'].required = False
        self.fields['patrono'].required = False
        self.fields['patronoCodigo'].required = False
        self.fields['fechaNacimiento'].required = False
        self.fields['movPrimerMes'].required = False
        self.fields['ingresosMes1'].required = False
        self.fields['egresosMes1'].required = False
        self.fields['ingresosMes2'].required = False
        self.fields['egresosMes2'].required = False
        self.fields['ingresosMes3'].required = False
        self.fields['egresosMes3'].required = False
        self.fields['ingresosMes4'].required = False
        self.fields['egresosMes4'].required = False
        self.fields['ingresosMes5'].required = False
        self.fields['egresosMes5'].required = False
        self.fields['ingresosMes6'].required = False
        self.fields['egresosMes6'].required = False
        self.fields['movOpcion'].required = False
        self.fields['averageIngresos'].required = False
        self.fields['tasaInteres'].required = False

