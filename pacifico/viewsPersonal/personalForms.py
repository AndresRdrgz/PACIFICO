
from django import forms
from ..models import Cotizacion, Aseguradora
from django.contrib.auth.models import User


from django.conf import settings

class PrestamoPersonalForm(forms.ModelForm):
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
           
            'pagaDiciembre': forms.Select(attrs={
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
            'porServDesc': forms.NumberInput(attrs={
                'placeholder': 'Porcentaje de Descuento por Servicio',
                'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
                
            }),
            'selectDescuento': forms.Select(attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
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
           
           
            'oficial': forms.Select(attrs={
                'placeholder': 'Oficial',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
            'sucursal': forms.Select(attrs={
                'placeholder': 'Sucursal',
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                
            }),
        
        }

    periodoPago = forms.ChoiceField(
        choices=[(1, 'MENSUAL'), (2, 'QUINCENAL')],
        initial=1,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-100 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2',
        })
    )
    formaPago = forms.ChoiceField(
        choices=[(1, '1 - PAGO VOLUNTARIO'), (2, '2 - DESCUENTO DIRECTO')],
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
        self.fields['patronoCodigo'].required = False
        self.fields['montoManejoT'].required = False
        self.fields['monto_manejo_b'].required = False
        self.fields['aplicaCodeudor'].required = False
        self.fields['tasaInteres'].required = False
        self.fields['porServDesc'].required = False
        self.fields['selectDescuento'].required = False
        

