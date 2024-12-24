import os
from django import forms
from .models import Cotizacion, Aseguradora, Cliente
from pathlib import Path
import json
from django.conf import settings

# Load the JSON file
BASE_DIR = Path(__file__).resolve().parent.parent
with open(BASE_DIR / 'static/insumos/autos.json') as f:
    choices_data = json.load(f)

# Extract unique values for the "MARCA" field
unique_marcas = list({item['MARCA'] for item in choices_data})

# Convert unique "MARCA" values to choices format
marca_choices = [(marca, marca) for marca in unique_marcas]

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
                'readonly': 'readonly',
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
        exclude = ['tasaInteres']
        
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
            'fechaNacimiento': forms.DateInput(attrs={
                'placeholder': 'Fecha de Inicio',
                'class': 'w-full text-slate-600 text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:border-blue-500',
                'type': 'date',
            }),
            'edad': forms.NumberInput(attrs={
                'placeholder': 'Edad',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'readonly': 'readonly',
            }),
            'sexo': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'jubilado': forms.Select(attrs={
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
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                #'initial': '1 - SIN VENDEDOR',
                'readonly': 'readonly',
                
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
            'totalIngresosAdicionales': forms.NumberInput(attrs={
                'placeholder': 'Total Ingresos Adicionales',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly': 'readonly',
            }),
            #DATOS DEL AUTO
            'marca':forms.TextInput(attrs={
                'placeholder': 'Marca del Auto',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'modelo':forms.TextInput(attrs={
                'placeholder': 'Modelo del Auto',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'yearsFinanciamiento': forms.NumberInput(attrs={
                'placeholder': 'Años de Financiamiento',
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
    tipoDocumento = forms.ChoiceField(
        choices=[('CEDULA', 'Cédula'), ('PASAPORTE', 'Pasaporte')],
        initial='CEDULA',
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    apcScore = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'APC Score',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    apcPI = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'APC PI',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
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
    transmisionAuto = forms.ChoiceField(
        choices=[('MANUAL', 'Manual'), ('AUTOMÁTICO', 'Automático')],
        initial='MANUAL',
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    nuevoAuto = forms.ChoiceField(
        choices=[('AUTO NUEVO', 'Auto Nuevo'), ('AUTO USADO', 'Auto Usado')],
        initial='AUTO NUEVO',
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    kilometrajeAuto = forms.IntegerField(
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Kilometraje del Vehículo',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    valorAuto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Valor del Vehículo',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )
    #ENDEUDAMIENTO
    horasExtrasMonto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Horas Extras Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )
    horasExtrasDcto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    primaMonto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Prima Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly': 'readonly',
        })
    )
    primaDcto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    bonosMonto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Bonos Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    bonosDcto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    otrosMonto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Otros Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    otrosDcto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    #descuento directo
    siacapMonto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'SIACAP Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    siacapDcto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    praaMonto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'PRAA Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    praaDcto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    dirOtros1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Otros',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosMonto1 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Otros Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosDcto1 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    dirOtros2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Otros',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosMonto2 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Otros Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosDcto2 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    dirOtros3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Otros',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosMonto3 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Otros Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosDcto3 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
    dirOtros4 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Otros',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosMonto4 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Otros Monto',
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    dirOtrosDcto4 = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded',
        })
    )
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
    #Datos del Codeudor
    codeudorEstabilidad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Estabilidad',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorIngresos = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ingresos',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorNombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre del Codeudor',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorCedula = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Cédula del Codeudor',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    #codeudorLicencia select field with Si or No
    codeudorLicencia = forms.ChoiceField(
        choices=[
            ('', 'Seleccione una opción'),
            ('SI', 'Sí'),
            ('NO', 'No')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorEmpresa = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de la Empresa',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorReferenciasAPC = forms.ChoiceField(
        choices=[
            ('', 'Seleccione una opción'),
            ('BUENAS', 'BUENAS'),
            ('REGULARES', 'REGULARES'),
            ('MALAS', 'MALAS'),
            ('PESIMAS', 'PESIMAS'),
            ('SIN REFERENCIAS', 'SIN REFERENCIAS')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorNombreEmpres1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de la Empresa',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorPeriodo1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Periodo',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorSalario1 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Salario',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorNombreEmpres2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de la Empresa',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorPeriodo2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Periodo',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorSalario2 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Salario',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorNombreEmpres3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de la Empresa',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorPeriodo3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Periodo',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    codeudorSalario3 = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Salario',
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
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
        self.fields['vendedor'].required = False
        self.fields['montoPrestamo'].required = False
        self.fields['fechaInicioPago'].required = False
        self.fields['salarioBaseMensual'].required = False
        self.fields['cashback'].required = False
        self.fields['abono'].required = False
        self.fields['abonoPorcentaje'].required = False
        self.fields['totalIngresosAdicionales'].required = False
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
       