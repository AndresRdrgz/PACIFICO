from django import forms
from .models import Cotizacion, Aseguradora

class FideicomisoForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        #fields all except tasaInteres
        exclude = ['tasaInteres']
        
        widgets = {
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
                'readonly' : 'readonly',
            }),
            'sexo': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'fechaInicioPago': forms.DateInput(attrs={
                'placeholder': 'Fecha de Inicio',
                'class': 'w-full text-slate-600 text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:border-blue-500',
                'type': 'date',
            }),
            'comiCierre': forms.NumberInput(attrs={
                'placeholder': 'Comisión de Cierre',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'plazoPago': forms.NumberInput(attrs={
                'placeholder': 'Plazo de Pago',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'montoPrestamo': forms.NumberInput(attrs={
                'placeholder': 'Monto del Préstamo',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'r_deseada': forms.NumberInput(attrs={
                'placeholder': 'R Deseada',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            }),
            'patrono': forms.TextInput(attrs={
                'placeholder': 'Patrono',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly' : 'readonly',
            }),
            'patronoCodigo': forms.NumberInput(attrs={
                'placeholder': 'Código del Patrono',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'readonly' : 'readonly',
            }),
            'vendedor': forms.TextInput(attrs={
                'placeholder': 'Vendedor',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                'initial': '1 - SIN VENDEDOR',
                'readonly' : 'readonly',
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
               'readonly' : 'readonly',
               'required': False,
            }),
            'cantPagosSeguro': forms.NumberInput(attrs={
                'placeholder': 'Cantidad de Pagos del Seguro',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'required': False,
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
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            
        })
    )
   
    aseguradora = forms.ModelChoiceField(
        queryset=Aseguradora.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    
    aseguradoraAuto = forms.ChoiceField(
        choices=[(6, 'SEGUROS SURAMERICANA, S.A.')],
        initial=6,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly' : 'readonly',
            
        })
    )
    corredorSeguro = forms.ChoiceField(
        choices=[(3, 'ROLKAM Y ASOCIADOS, S.A.')],
        initial=3,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly' : 'readonly',
            
        })
    )
    #tipoSeguro with the choices Incluido and No Incluido
    tipoSeguro = forms.ChoiceField(
        choices=[('INCLUIDO', 'Incluido'), ('NO INCLUIDO', 'No Incluido')],
        initial='INCLUIDO',
        widget=forms.Select(attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
        })
    )
    #frecuenciaPagoSeguro with only 1 choice = "MENSUAL"
    frecuenciaPagoSeguro = forms.ChoiceField(
        choices=[('MENSUAL', 'MENSUAL')],
        initial='MENSUAL',
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly' : 'readonly',
            
        })
    )
    # aseguradora with two choices, 7 - INTERNACIONAL DE SEGUROS - FIDEICOMISO H and 8 - INTERNACIONAL DE SEGUROS - FIDEICOMISO M7 - INTERNACIONAL DE SEGUROS - FIDEICOMISO H
    '''aseguradora = forms.ChoiceField(
        choices=[(7, 'INTERNACIONAL DE SEGUROS - FIDEICOMISO H'), (8, 'INTERNACIONAL DE SEGUROS - FIDEICOMISO M')],
        initial=7,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
            'readonly' : 'readonly',
            
        })
    )
    '''
    