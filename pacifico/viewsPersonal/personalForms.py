
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
        self.fields['porServDesc'].required = False
        self.fields['selectDescuento'].required = False

