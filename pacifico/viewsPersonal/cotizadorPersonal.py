import logging
import sys
from ..models import CotizacionDocumento, UserProfile, Cotizacion, Aseguradora

from django.shortcuts import get_object_or_404


from decimal import Decimal
import datetime
from django.shortcuts import render, redirect
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .personalForms import PrestamoPersonalForm
from ..prestamoPersonal.calculoPP import generarPP
import pprint
from ..viewsFideicomiso.cotizadorFideicomiso import prepResultado, aplicaCodeudor, set_calculated_values, convert_decimal_to_float, set_calculated_values2, calculoInicial

from ..analisisConsulta.nivelEndeudamiento import nivelEndeudamiento  # Corrected import statement
from ..views import log_error


def identifica_seguro(patrono, sucursal):
    aseguradora = 0
    print("Identificando aseguradora, patrono: ", patrono, "sucursal: ", sucursal)

    if 638 <= patrono <= 657:
        #TT
        if patrono in [638, 642, 643, 649, 650]:
            #TTT
            if sucursal in [2,4,13,24,26,8]:
                #TTTT
                aseguradora = 100
        elif patrono == 640:
            #TTFT
            if sucursal == 2:
                #TTFTT
                aseguradora = 19
        else:
            #TTFT
            if sucursal in [2,4,13,24,26,7,8]:
                #TTFTT
                aseguradora = 4
    else:
        #TF
        if sucursal == 4:
            #TFT
            aseguradora = 20
        elif sucursal in [2, 13, 24, 26, 8,11, 7]:
            #TFT
            aseguradora = 19

    print("REsultado aseguradora: ", aseguradora)
    try:
        aseguradora_obj = Aseguradora.objects.get(codigo=aseguradora)
        print("Encontrada aseguradora: ", aseguradora_obj)
        print(f"aseguradora {aseguradora_obj.codigo} - {aseguradora_obj.descripcion} type: {type(aseguradora_obj)}")
    except Aseguradora.DoesNotExist:
        print(f"No aseguradora found with codigo: {aseguradora}")

    return aseguradora




logger = logging.getLogger(__name__)
@login_required
def cotizacionPrestamoPersonal(request, pk=None):
    resultado = None
    cotizacion = None
    print("cotizacionPrestamoPersonal, pk:", pk)
    if pk:
        cotizacion = get_object_or_404(Cotizacion, pk=pk)
        resultado = prepResultado(cotizacion)
        print("cotizacion:", cotizacion)

    if request.method == 'POST':
        form = PrestamoPersonalForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            try:
                # Extract form data and perform calculations (existing logic)
                # ...existing code...
                
                edad = form.cleaned_data['edad']
                sexo = form.cleaned_data['sexo']
                jubilado = form.cleaned_data['jubilado']
                aplicaPromocion = form.cleaned_data['aplicaPromocion']
                nombreCliente = form.cleaned_data['nombreCliente']
                cotMontoPrestamo = Decimal(form.cleaned_data['montoPrestamo'])
                calcTasaInteres = 10 / 100
                if form.cleaned_data['tasaInteres'] is not None:
                    calcTasaInteres = Decimal(form.cleaned_data['tasaInteres']) / 100
                print("tasa interes",calcTasaInteres)
               
                calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
                auxPlazoPago = form.cleaned_data['plazoPago']
                patrono = form.cleaned_data['patronoCodigo']
                fecha_inicioPago = form.cleaned_data['fechaInicioPago']
                porServDesc = form.cleaned_data['porServDesc'] if form.cleaned_data['porServDesc'] is not None else 0
                selectDescuento = form.cleaned_data['selectDescuento']
                periodoPago = form.cleaned_data['periodoPago']

                if patrono is None: patrono = 9999

                sucursal = form.cleaned_data['sucursal']
                auxPeriocidad = int(periodoPago)
                formaPago = form.cleaned_data['formaPago']
                print("formaPago", formaPago, type(formaPago))
                if formaPago == '2':
                    forma_pago = 3
                else:
                    forma_pago = 4

                print("forma_pago",forma_pago)
                
                
                r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
                #datos comision vendedor
                comisionVendedor = form.cleaned_data['vendedorComision'] if form.cleaned_data['vendedorComision'] is not None else 0
                vendedorOtroComision = form.cleaned_data['vendedorOtroComision'] if form.cleaned_data['vendedorOtroComision'] is not None else 0
                vendedorTipo = form.cleaned_data['vendedorTipo']
                vendedorComisionPorcentaje = form.cleaned_data['vendedorComisionPorcentaje'] if form.cleaned_data['vendedorComisionPorcentaje'] is not None else 0
                vendedorOtroPorcentaje = form.cleaned_data['vendedorOtroPorcentaje'] if form.cleaned_data['vendedorOtroPorcentaje'] is not None else 0
                
                #datos cancelaciones
                cancDescripcion1 = form.cleaned_data['cancDescripcion1'] if form.cleaned_data['cancDescripcion1'] is not None else "-"
                cancMonto1 = form.cleaned_data['cancMonto1'] if form.cleaned_data['cancMonto1'] is not None else 0
                cancMensualidad1 = form.cleaned_data['cancMensualidad1'] if form.cleaned_data['cancMensualidad1'] is not None else 0
                cancDescripcion2 = form.cleaned_data['cancDescripcion2'] if form.cleaned_data['cancDescripcion2'] is not None else "-"
                cancMonto2 = form.cleaned_data['cancMonto2'] if form.cleaned_data['cancMonto2'] is not None else 0
                cancMensualidad2 = form.cleaned_data['cancMensualidad2'] if form.cleaned_data['cancMensualidad2'] is not None else 0
                cancDescripcion3 = form.cleaned_data['cancDescripcion3'] if form.cleaned_data['cancDescripcion3'] is not None else "-"
                cancMonto3 = form.cleaned_data['cancMonto3'] if form.cleaned_data['cancMonto3'] is not None else 0
                cancMensualidad3 = form.cleaned_data['cancMensualidad3'] if form.cleaned_data['cancMensualidad3'] is not None else 0
                cancDescripcion4 = form.cleaned_data['cancDescripcion4'] if form.cleaned_data['cancDescripcion4'] is not None else "-"
                cancMonto4 = form.cleaned_data['cancMonto4'] if form.cleaned_data['cancMonto4'] is not None else 0
                cancMensualidad4 = form.cleaned_data['cancMensualidad4'] if form.cleaned_data['cancMensualidad4'] is not None else 0
                cancDescripcion5 = form.cleaned_data['cancDescripcion5'] if form.cleaned_data['cancDescripcion5'] is not None else "-"
                cancMonto5 = form.cleaned_data['cancMonto5'] if form.cleaned_data['cancMonto5'] is not None else 0
                cancMensualidad5 = form.cleaned_data['cancMensualidad5'] if form.cleaned_data['cancMensualidad5'] is not None else 0
                
                cancRefiSaldo = form.cleaned_data['cancRefiSaldo'] if form.cleaned_data['cancRefiSaldo'] is not None else 0
                calcNetoCancelacion = cancMonto1 + cancMonto2 + cancMonto3 + cancMonto4 + cancMonto5 + cancRefiSaldo

                form.instance.cancDescripcion1 = cancDescripcion1
                form.instance.cancMonto1 = cancMonto1
                form.instance.cancMensualidad1 = cancMensualidad1
                form.instance.cancDescripcion2 = cancDescripcion2
                form.instance.cancMonto2 = cancMonto2
                form.instance.cancMensualidad2 = cancMensualidad2
                form.instance.cancDescripcion3 = cancDescripcion3
                form.instance.cancMonto3 = cancMonto3
                form.instance.cancMensualidad3 = cancMensualidad3
                form.instance.cancDescripcion4 = cancDescripcion4
                form.instance.cancMonto4 = cancMonto4
                form.instance.cancMensualidad4 = cancMensualidad4
                form.instance.cancDescripcion5 = cancDescripcion5
                form.instance.cancMonto5 = cancMonto5
                form.instance.cancMensualidad5 = cancMensualidad5


                cantPagosSeguro = form.cleaned_data['cantPagosSeguro']
                sucursal = form.cleaned_data['sucursal']

                cotMontoPrestamo = float(cotMontoPrestamo)
                calcTasaInteres = float(calcTasaInteres)
                calcComiCierre = float(calcComiCierre)
                r_deseada = float(r_deseada)
                comisionVendedor = float(comisionVendedor)
                sucursal = int(sucursal)
                pagaDiciembre = form.cleaned_data['pagaDiciembre']

                print("--------calculando aseguradora---------")
                codigoSeguro = identifica_seguro(patrono, sucursal)
                params = {
                    'tipoPrestamo': 'PERSONAL',
                    'edad': edad,
                    'sucursal': sucursal,
                    'sexo': sexo,
                    'jubilado': jubilado,
                    'cotMontoPrestamo': cotMontoPrestamo,
                    'fecha_inicioPago': fecha_inicioPago,
                    'calcTasaInteres': calcTasaInteres,
                    'calcComiCierre': calcComiCierre,
                    'auxPlazoPago': auxPlazoPago,
                    'patrono': patrono,
                    'sucursal': sucursal,
                    'auxPeriocidad': auxPeriocidad,
                    'forma_pago': forma_pago,
                    'codigoSeguro': codigoSeguro,
                    'fechaCalculo': datetime.datetime.now(),
                    'r_deseada': r_deseada,
                    'comisionVendedor': comisionVendedor,
                    'porServDesc': porServDesc,
                    'selectDescuento': selectDescuento,
                    'pagaDiciembre': pagaDiciembre,
                    'vendedorTipo': vendedorTipo,
                    'vendedorOtroComision': vendedorOtroComision,
                    'vendedorComisionPorcentaje': float(vendedorComisionPorcentaje),
                    'vendedorOtroPorcentaje': float(vendedorOtroPorcentaje),
                    'calcNetoCancelacion': float(calcNetoCancelacion),
                    'aplicaPromocion': aplicaPromocion,
                }
                print("params",params)
                
                resultado, iteration_data = generarPP(params)
                print("--------finalizado---------")
                resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra'] / 2, 2) * 2
                #Preparacion campos nivel
                #Datos del deudor
                resultado['tiempoServicio'] = form.cleaned_data['tiempoServicio'] if form.cleaned_data['tiempoServicio'] is not None else "-"
                resultado['ingresos'] = form.cleaned_data['ingresos'] if form.cleaned_data['ingresos'] is not None else 0
                resultado['nombreEmpresa'] = form.cleaned_data['nombreEmpresa'] if form.cleaned_data['nombreEmpresa'] is not None else "-"
                resultado['referenciasAPC'] = form.cleaned_data['referenciasAPC'] if form.cleaned_data['referenciasAPC'] is not None else "-"
                resultado['cartera'] = form.cleaned_data['cartera'] if form.cleaned_data['cartera'] is not None else "-"
                resultado['licencia'] = form.cleaned_data['licencia'] if form.cleaned_data['licencia'] is not None else "-"
                resultado['posicion'] = form.cleaned_data['posicion'] if form.cleaned_data['posicion'] is not None else "-"
                resultado['perfilUniversitario'] = form.cleaned_data['perfilUniversitario'] if form.cleaned_data['perfilUniversitario'] is not None else "-"

                #DATOS NIVEL DE ENDEUDAMIENTO
                resultado['salarioBaseMensual'] = form.cleaned_data['salarioBaseMensual'] if form.cleaned_data['salarioBaseMensual'] is not None else 0
                resultado['horasExtrasMonto'] = form.cleaned_data['horasExtrasMonto'] if form.cleaned_data['horasExtrasMonto'] is not None else 0
                resultado['horasExtrasDcto'] = form.cleaned_data['horasExtrasDcto'] if form.cleaned_data['horasExtrasDcto'] is not None else 0
                resultado['primaMonto'] = form.cleaned_data['primaMonto'] if form.cleaned_data['primaMonto'] is not None else 0
                resultado['primaDcto'] = form.cleaned_data['primaDcto'] if form.cleaned_data['primaDcto'] is not None else 0
                resultado['bonosMonto'] = form.cleaned_data['bonosMonto'] if form.cleaned_data['bonosMonto'] is not None else 0
                resultado['bonosDcto'] = form.cleaned_data['bonosDcto'] if form.cleaned_data['bonosDcto'] is not None else 0
                resultado['otrosMonto'] = form.cleaned_data['otrosMonto'] if form.cleaned_data['otrosMonto'] is not None else 0
                resultado['otrosDcto'] = form.cleaned_data['otrosDcto'] if form.cleaned_data['otrosDcto'] is not None else 0

                #DESCUENTO DIRECTO
                resultado['siacapMonto'] = form.cleaned_data['siacapMonto'] if form.cleaned_data['siacapMonto'] is not None else 0
                resultado['siacapDcto'] = form.cleaned_data['siacapDcto'] if form.cleaned_data['siacapDcto'] is not None else False
                resultado['praaMonto'] = form.cleaned_data['praaMonto'] if form.cleaned_data['praaMonto'] is not None else 0
                resultado['praaDcto'] = form.cleaned_data['praaDcto'] if form.cleaned_data['praaDcto'] is not None else False
                resultado['dirOtrosMonto1'] = form.cleaned_data['dirOtrosMonto1'] if form.cleaned_data['dirOtrosMonto1'] is not None else 0
                resultado['dirOtros1'] = form.cleaned_data['dirOtros1'] if form.cleaned_data['dirOtros1'] is not None else "-"
                resultado['dirOtrosDcto1'] = form.cleaned_data['dirOtrosDcto1'] if form.cleaned_data['dirOtrosDcto1'] is not None else False
                resultado['dirOtrosMonto2'] = form.cleaned_data['dirOtrosMonto2'] if form.cleaned_data['dirOtrosMonto2'] is not None else 0
                resultado['dirOtros2'] = form.cleaned_data['dirOtros2'] if form.cleaned_data['dirOtros2'] is not None else "-"
                resultado['dirOtrosDcto2'] = form.cleaned_data['dirOtrosDcto2'] if form.cleaned_data['dirOtrosDcto2'] is not None else False
                resultado['dirOtrosMonto3'] = form.cleaned_data['dirOtrosMonto3'] if form.cleaned_data['dirOtrosMonto3'] is not None else 0
                resultado['dirOtros3'] = form.cleaned_data['dirOtros3'] if form.cleaned_data['dirOtros3'] is not None else "-"
                resultado['dirOtrosDcto3'] = form.cleaned_data['dirOtrosDcto3'] if form.cleaned_data['dirOtrosDcto3'] is not None else False
                resultado['dirOtrosMonto4'] = form.cleaned_data['dirOtrosMonto4'] if form.cleaned_data['dirOtrosMonto4'] is not None else 0
                resultado['dirOtros4'] = form.cleaned_data['dirOtros4'] if form.cleaned_data['dirOtros4'] is not None else "-"
                resultado['dirOtrosDcto4'] = form.cleaned_data['dirOtrosDcto4'] if form.cleaned_data['dirOtrosDcto4'] is not None else False


                #PAGO VOLUNTARIO
                resultado['pagoVoluntario1'] = form.cleaned_data['pagoVoluntario1'] if form.cleaned_data['pagoVoluntario1'] is not None else 0
                resultado['pagoVoluntarioMonto1'] = form.cleaned_data['pagoVoluntarioMonto1'] if form.cleaned_data['pagoVoluntarioMonto1'] is not None else 0
                resultado['pagoVoluntarioDcto1'] = form.cleaned_data['pagoVoluntarioDcto1'] if form.cleaned_data['pagoVoluntarioDcto1'] is not None else 0
                resultado['pagoVoluntario2'] = form.cleaned_data['pagoVoluntario2'] if form.cleaned_data['pagoVoluntario2'] is not None else 0
                resultado['pagoVoluntarioMonto2'] = form.cleaned_data['pagoVoluntarioMonto2'] if form.cleaned_data['pagoVoluntarioMonto2'] is not None else 0
                resultado['pagoVoluntarioDcto2'] = form.cleaned_data['pagoVoluntarioDcto2'] if form.cleaned_data['pagoVoluntarioDcto2'] is not None else 0
                resultado['pagoVoluntario3'] = form.cleaned_data['pagoVoluntario3'] if form.cleaned_data['pagoVoluntario3'] is not None else 0
                resultado['pagoVoluntarioMonto3'] = form.cleaned_data['pagoVoluntarioMonto3'] if form.cleaned_data['pagoVoluntarioMonto3'] is not None else 0
                resultado['pagoVoluntarioDcto3'] = form.cleaned_data['pagoVoluntarioDcto3'] if form.cleaned_data['pagoVoluntarioDcto3'] is not None else 0
                resultado['pagoVoluntario4'] = form.cleaned_data['pagoVoluntario4'] if form.cleaned_data['pagoVoluntario4'] is not None else 0
                resultado['pagoVoluntarioMonto4'] = form.cleaned_data['pagoVoluntarioMonto4'] if form.cleaned_data['pagoVoluntarioMonto4'] is not None else 0
                resultado['pagoVoluntarioDcto4'] = form.cleaned_data['pagoVoluntarioDcto4'] if form.cleaned_data['pagoVoluntarioDcto4'] is not None else 0
                resultado['pagoVoluntario5'] = form.cleaned_data['pagoVoluntario5'] if form.cleaned_data['pagoVoluntario5'] is not None else 0
                resultado['pagoVoluntarioMonto5'] = form.cleaned_data['pagoVoluntarioMonto5'] if form.cleaned_data['pagoVoluntarioMonto5'] is not None else 0
                resultado['pagoVoluntarioDcto5'] = form.cleaned_data['pagoVoluntarioDcto5'] if form.cleaned_data['pagoVoluntarioDcto5'] is not None else 0
                resultado['pagoVoluntario6'] = form.cleaned_data['pagoVoluntario6'] if form.cleaned_data['pagoVoluntario6'] is not None else 0
                resultado['pagoVoluntarioMonto6'] = form.cleaned_data['pagoVoluntarioMonto6'] if form.cleaned_data['pagoVoluntarioMonto6'] is not None else 0
                resultado['pagoVoluntarioDcto6'] = form.cleaned_data['pagoVoluntarioDcto6'] if form.cleaned_data['pagoVoluntarioDcto6'] is not None else 0
                
                resultado['horasExtrasMonto'] = form.cleaned_data['horasExtrasMonto'] if form.cleaned_data['horasExtrasMonto'] is not None else 0  
                #PRORRATEO
                resultado['mes0'] = form.cleaned_data['mes0'] if form.cleaned_data['mes0'] is not None else 0
                resultado['mes1'] = form.cleaned_data['mes1'] if form.cleaned_data['mes1'] is not None else 0
                resultado['mes2'] = form.cleaned_data['mes2'] if form.cleaned_data['mes2'] is not None else 0
                resultado['mes3'] = form.cleaned_data['mes3'] if form.cleaned_data['mes3'] is not None else 0
                resultado['mes4'] = form.cleaned_data['mes4'] if form.cleaned_data['mes4'] is not None else 0
                resultado['mes5'] = form.cleaned_data['mes5'] if form.cleaned_data['mes5'] is not None else 0
                resultado['mes6'] = form.cleaned_data['mes6'] if form.cleaned_data['mes6'] is not None else 0
                resultado['mes7'] = form.cleaned_data['mes7'] if form.cleaned_data['mes7'] is not None else 0
                resultado['mes8'] = form.cleaned_data['mes8'] if form.cleaned_data['mes8'] is not None else 0
                resultado['mes9'] = form.cleaned_data['mes9'] if form.cleaned_data['mes9'] is not None else 0
                resultado['mes10'] = form.cleaned_data['mes10'] if form.cleaned_data['mes10'] is not None else 0
                resultado['mes11'] = form.cleaned_data['mes11'] if form.cleaned_data['mes11'] is not None else 0
                resultado['primerMes'] = form.cleaned_data['primerMes'] if form.cleaned_data['primerMes'] is not None else ""
                resultado['tipoProrrateo'] = form.cleaned_data['tipoProrrateo'] if form.cleaned_data['tipoProrrateo'] is not None else ""
                #print('primer mes', resultado['primerMes'],form.cleaned_data['primerMes'])
                # MONTO LETRA SIN SEGUROS
                resultado['montoMensualSeguro'] = form.cleaned_data['montoMensualSeguro'] if form.cleaned_data['montoMensualSeguro'] is not None else 0
                resultado['wrkLetraSinSeguros'] = resultado['wrkMontoLetra']  - resultado['wrkLetraSeguro']
                resultado['wrkLetraSinSeguros'] = round(resultado['wrkLetraSinSeguros'], 2)
                resultado['wrkLetraConSeguros'] = resultado['wrkMontoLetra'] + resultado['montoMensualSeguro']
                resultado['wrkLetraConSeguros'] = round(resultado['wrkLetraConSeguros'], 2)
                resultado['calcComiCierreFinal'] = round(resultado['calcComiCierreFinal'], 2)
                
                resultado['cashback'] = form.cleaned_data['cashback'] if form.cleaned_data['cashback'] is not None else 0
                resultado['cashback'] = round(resultado['cashback'], 2)
                resultado['r1']=round(resultado['r1'],2)
                resultado['abono'] = form.cleaned_data['abono'] if form.cleaned_data['abono'] is not None else 0
                resultado['abono'] = round(resultado['abono'], 2)
                resultado['abonoPorcentaje'] = form.cleaned_data['abonoPorcentaje'] if form.cleaned_data['abonoPorcentaje'] is not None else 0
                resultado['abonoPorcentaje'] = round(resultado['abonoPorcentaje'], 2)
                #CALCULO NIVEL DE ENDEUDAMIENTO - REAL
                print("CALCULO NIVEL DE ENDEUDAMIENTO - REAL")
                resultado = convert_decimal_to_float(resultado)
                resultadoNivel = nivelEndeudamiento(resultado)
                resultado['salarioNeto'] = resultadoNivel['salarioNeto']
                resultado['porSalarioNeto'] = resultadoNivel['porSalarioNeto']
                resultado['salarioNetoActual'] = resultadoNivel['salarioNetoActual']
                resultado['totalIngresosAdicionales'] = round(resultadoNivel['totalIngresosAdicionales'],2)
                resultado['totalIngresosMensuales'] = resultadoNivel['totalIngresosMensuales']
                resultado['totalDescuentoDirecto'] = resultadoNivel['totalDescuentoDirecto']
                resultado['totalPagoVoluntario'] = resultadoNivel['totalPagoVoluntario']
                resultado['totalDescuentosLegales'] = resultadoNivel['totalDescuentosLegales']
                #nivel de endeudamiento - completo
                resultado['totalIngresosMensualesCompleto'] = resultadoNivel['totalIngresosMensualesCompleto']
                resultado['totalDescuentosLegalesCompleto'] = resultadoNivel['totalDescuentosLegalesCompleto']
                resultado['salarioNetoActualCompleto'] = resultadoNivel['salarioNetoActualCompleto']
                resultado['salarioNetoCompleto'] = resultadoNivel['salarioNetoCompleto']
                resultado['porSalarioNetoCompleto'] = resultadoNivel['porSalarioNetoCompleto']
                resultado['porcentajeLetraSeguro'] = round(((resultado['wrkMontoLetra'] + resultado['montoMensualSeguro']) / resultado['salarioBaseMensual'] * 100), 2) if resultado['salarioBaseMensual'] not in [None, 0] else 0
                print("Nivel de endeudamiento - completo")

                # Convert datetime.date objects to strings
                for key, value in resultado.items():
                    if isinstance(value, datetime.date):
                        resultado[key] = value.strftime('%Y-%m-%d')

                form.instance.tasaEstimada = resultado['tasaEstimada']
                form.instance.tasaBruta = resultado['tasaBruta']
                form.instance.r1 = resultado['r1']
                form.instance.montoPrestamo = resultado['cotMontoPrestamo']
                form.instance.auxMonto2 = round(Decimal(resultado['auxMonto2']), 2)
                form.instance.montoManejoT = resultado['montoManejoT']
                form.instance.monto_manejo_b = resultado['montoManejoB']
                form.instance.wrkMontoLetra = resultado['wrkMontoLetra']
                form.instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
                form.instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
                form.instance.calcMontoNotaria = resultado['calcMontoNotaria']
                form.instance.calcMontoTimbres = resultado['calcMontoTimbres']
                form.instance.tablaTotalPagos = resultado['tablaTotalPagos']
                form.instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
                form.instance.tablaTotalFeci = resultado['tablaTotalFeci']
                form.instance.tablaTotalInteres = resultado['tablaTotalInteres']
                form.instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
                form.instance.manejo_5porc = resultado['manejo_5porc']
                form.instance.added_by = request.user if request.user.is_authenticated else "INVITADO"

                #GUARDAR DATOS NIVEL
                form.instance.otrosMonto = resultado['otrosMonto']
                form.instance.bonosMonto = resultado['bonosMonto']
                form.instance.primaMonto = resultado['primaMonto']
                form.instance.salarioBaseMensual = resultado['salarioBaseMensual']
                form.instance.totalDescuentosLegales = resultado['totalDescuentosLegales']
                form.instance.totalDescuentoDirecto = resultado['totalDescuentoDirecto']
                form.instance.totalPagoVoluntario = resultado['totalPagoVoluntario']
                form.instance.salarioNetoActual = resultado['salarioNetoActual']
                form.instance.salarioNeto = resultado['salarioNeto']
                form.instance.porSalarioNeto = resultado['porSalarioNeto']
                form.instance.totalIngresosAdicionales = resultado['totalIngresosAdicionales']
                form.instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
                form.instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
                form.instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
                form.instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
                form.instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']


                form.instance.tipoPrestamo = 'personal'
                codigoSeguro = resultado['codigoSeguro']
                aseguradora = Aseguradora.objects.get(codigo=codigoSeguro)
                print("nueva instancia aseguradora:", aseguradora,"codigoSeguro:", resultado['codigoSeguro'])
                
                form.instance.aseguradora = aseguradora

                #letra mensual
                if resultado['auxPeriocidad'] == 2:
                    resultado['wrkMontoLetraMensual'] = resultado['wrkMontoLetra'] * 2
                else:
                    resultado['wrkMontoLetraMensual'] = resultado['wrkMontoLetra']
                

                form.save()
                print("se guardo -",form.instance.pk)
                numero_cotizacion = int(form.instance.pk)
                resultado['numero_cotizacion'] = numero_cotizacion
                for key, value in resultado.items():
                            if isinstance(value, Decimal):
                                resultado[key] = float(value)
                request.session['resultado'] = resultado
                print("redirecting,", numero_cotizacion)
                messages.success(request, 'Cotización guardada exitosamente.')
                return redirect('prestPersonal_with_pk', pk=form.instance.pk)

            except Exception as e:
                logger.error("Error in prest personal: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
                print(e)
        else:
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
    else:
        form = PrestamoPersonalForm(instance=cotizacion)

        if not cotizacion:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.sucursal is not None:
                form.fields['sucursal'].initial = user_profile.sucursal

            if user_profile.oficial is not None:
                form.fields['oficial'].initial = user_profile.oficial

    context = {
        'form': form,
        'resultado': resultado,
        'cotizacion': cotizacion,
        
    }

    if hasattr(request.user, 'userprofile') and request.user.userprofile.pruebaFuncionalidades:
        context['pruebaFuncionalidades'] = True

    return render(request, 'prestamoPersonal.html', context)


def perform_pp_calculation(form):
    print("-----------------perform_pp_calculation-----------------")
    # Extract form data
    try:
        # Extract form data
        edad = form.cleaned_data['edad']
        sexo = form.cleaned_data['sexo']
        jubilado = form.cleaned_data['jubilado']
        nombreCliente = form.cleaned_data['nombreCliente']
        cotMontoPrestamo = Decimal(form.cleaned_data['montoPrestamo'])
        
        calcTasaInteres = 10 / 100
        if form.cleaned_data['tasaInteres'] is not None:
            calcTasaInteres = Decimal(form.cleaned_data['tasaInteres']) / 100
        print("tasa interes",calcTasaInteres)
        calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
        auxPlazoPago = form.cleaned_data['plazoPago']
        patrono = form.cleaned_data['patronoCodigo'] if form.cleaned_data['patronoCodigo'] is not None else 9999
        fecha_inicioPago = form.cleaned_data['fechaInicioPago']
        sucursal = 13
        porServDesc = form.cleaned_data['porServDesc'] if form.cleaned_data['porServDesc'] is not None else 0
        selectDescuento = form.cleaned_data['selectDescuento']
        periodoPago = form.cleaned_data['periodoPago']
        
        auxPeriocidad = int(periodoPago)
        forma_pago = 4
        # COLECTIVO DE CREDITO
        
        
        
        r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
        comisionVendedor = form.cleaned_data['vendedorComision']
        
        selectDescuento = form.cleaned_data['selectDescuento']
        pagaDiciembre = form.cleaned_data['pagaDiciembre']
        porServDesc = form.cleaned_data['porServDesc'] if form.cleaned_data['porServDesc'] is not None else 0
        sucursal = form.cleaned_data['sucursal']
        aplicaPromocion = form.cleaned_data['aplicaPromocion']
        

        # parse cotMontoPRestamo to float
        cotMontoPrestamo = float(cotMontoPrestamo)
        calcTasaInteres = float(calcTasaInteres)
        calcComiCierre = float(calcComiCierre)
        r_deseada = float(r_deseada)
        
        comisionVendedor = form.cleaned_data['vendedorComision'] if form.cleaned_data['vendedorComision'] is not None else 0
        vendedorOtroComision = form.cleaned_data['vendedorOtroComision'] if form.cleaned_data['vendedorOtroComision'] is not None else 0
        vendedorTipo = form.cleaned_data['vendedorTipo']
        vendedorComisionPorcentaje = form.cleaned_data['vendedorComisionPorcentaje'] if form.cleaned_data['vendedorComisionPorcentaje'] is not None else 0
        vendedorOtroPorcentaje = form.cleaned_data['vendedorOtroPorcentaje'] if form.cleaned_data['vendedorOtroPorcentaje'] is not None else 0
         #datos cancelaciones
        cancDescripcion1 = form.cleaned_data['cancDescripcion1'] if form.cleaned_data['cancDescripcion1'] is not None else "-"
        cancMonto1 = form.cleaned_data['cancMonto1'] if form.cleaned_data['cancMonto1'] is not None else 0
        cancMensualidad1 = form.cleaned_data['cancMensualidad1'] if form.cleaned_data['cancMensualidad1'] is not None else 0
        cancDescripcion2 = form.cleaned_data['cancDescripcion2'] if form.cleaned_data['cancDescripcion2'] is not None else "-"
        cancMonto2 = form.cleaned_data['cancMonto2'] if form.cleaned_data['cancMonto2'] is not None else 0
        cancMensualidad2 = form.cleaned_data['cancMensualidad2'] if form.cleaned_data['cancMensualidad2'] is not None else 0
        cancDescripcion3 = form.cleaned_data['cancDescripcion3'] if form.cleaned_data['cancDescripcion3'] is not None else "-"
        cancMonto3 = form.cleaned_data['cancMonto3'] if form.cleaned_data['cancMonto3'] is not None else 0
        cancMensualidad3 = form.cleaned_data['cancMensualidad3'] if form.cleaned_data['cancMensualidad3'] is not None else 0
        cancDescripcion4 = form.cleaned_data['cancDescripcion4'] if form.cleaned_data['cancDescripcion4'] is not None else "-"
        cancMonto4 = form.cleaned_data['cancMonto4'] if form.cleaned_data['cancMonto4'] is not None else 0
        cancMensualidad4 = form.cleaned_data['cancMensualidad4'] if form.cleaned_data['cancMensualidad4'] is not None else 0
        cancDescripcion5 = form.cleaned_data['cancDescripcion5'] if form.cleaned_data['cancDescripcion5'] is not None else "-"
        cancMonto5 = form.cleaned_data['cancMonto5'] if form.cleaned_data['cancMonto5'] is not None else 0
        cancMensualidad5 = form.cleaned_data['cancMensualidad5'] if form.cleaned_data['cancMensualidad5'] is not None else 0
        cancRefiSaldo = form.cleaned_data['cancRefiSaldo'] if form.cleaned_data['cancRefiSaldo'] is not None else 0
        calcNetoCancelacion = cancMonto1 + cancMonto2 + cancMonto3 + cancMonto4 + cancMonto5 + cancRefiSaldo

        sucursal = int(sucursal)
    
        #print('Sucursal', sucursal)
        # Call the generarFideicomiso2 function
        print("--------calculando aseguradora---------")
        codigoSeguro = identifica_seguro(patrono, sucursal)
        
        
        
        print("--------iniciando---------")
        params = {
            'tipoPrestamo': 'PERSONAL',
            'edad': edad,
            'sucursal': sucursal,
            'sexo': sexo,
            'jubilado': jubilado,
            'cotMontoPrestamo': cotMontoPrestamo,
            'fecha_inicioPago': fecha_inicioPago,
            'calcTasaInteres': calcTasaInteres,
            'calcComiCierre': calcComiCierre,
            'auxPlazoPago': auxPlazoPago,
            'patrono': patrono,
            'sucursal': sucursal,
            'auxPeriocidad': auxPeriocidad,
            'forma_pago': forma_pago,
            'codigoSeguro': codigoSeguro,
            'fechaCalculo': datetime.datetime.now(),
            'r_deseada': r_deseada,
            'comisionVendedor': comisionVendedor,
            'porServDesc': porServDesc,
            'selectDescuento': selectDescuento,
            'pagaDiciembre': pagaDiciembre,
            'vendedorTipo': vendedorTipo,
            'vendedorOtroComision': vendedorOtroComision,
            'vendedorComisionPorcentaje': float(vendedorComisionPorcentaje),
            'vendedorOtroPorcentaje': float(vendedorOtroPorcentaje),
            'calcNetoCancelacion': float(calcNetoCancelacion),
        }
        print('RESULTADO PARAMETROS', params)
        
        resultado, iteration_data = generarPP(params)
        print("--------finalizado---------")
   
        #print("--------finalizado---------")
        resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra']/2,2) * 2
        # #print in ta table format reusltado
        

        ##print(form.cleaned_data)
        #deserialize fechaCalculo in resultado
        resultado['fechaCalculo'] = resultado['fechaCalculo'].strftime('%Y-%m-%d')
        resultado['cotFechaInicioPago'] = resultado['cotFechaInicioPago'].strftime('%Y-%m-%d')
        resultado['calcFechaPromeCK'] = resultado['calcFechaPromeCK'].strftime('%Y-%m-%d')

        #PASE DE CAMPOS
        resultado['oficial'] = form.cleaned_data['oficial'] if form.cleaned_data['oficial'] is not None else "-"
        resultado['sucursal'] = form.cleaned_data['sucursal'] if form.cleaned_data['sucursal'] is not None else "-"
        resultado['sexo'] = sexo
        resultado['nombreCliente'] = form.cleaned_data['nombreCliente'] if form.cleaned_data['nombreCliente'] is not None else "-"
        resultado['cedulaCliente'] = form.cleaned_data['cedulaCliente'] if form.cleaned_data['cedulaCliente'] is not None else "-"
        
        resultado['calcComiCierreFinal'] = resultado['calcComiCierreFinal'] * 100
        
        resultado['tipoDocumento'] = form.cleaned_data['tipoDocumento'] if form.cleaned_data['tipoDocumento'] is not None else "-"
        resultado['apcScore'] = form.cleaned_data['apcScore'] if form.cleaned_data['apcScore'] is not None else "-"
        resultado['apcPI'] = form.cleaned_data['apcPI'] / 100 if form.cleaned_data['apcPI'] is not None else 0
        resultado['valorAuto'] = form.cleaned_data['valorAuto'] if form.cleaned_data['valorAuto'] is not None else 0
        resultado['cotPlazoPago'] = auxPlazoPago if auxPlazoPago is not None else 0
        resultado['vendedor'] = form.cleaned_data['vendedor'] if form.cleaned_data['vendedor'] is not None else "-"
        #DATOS DEL AUTO
        resultado['marcaAuto'] = form.cleaned_data['marca'] if form.cleaned_data['marca'] is not None else "-"
        resultado['lineaAuto'] = form.cleaned_data['modelo'] if form.cleaned_data['modelo'] is not None else "-"
        resultado['yearAuto'] = form.cleaned_data['yearCarro'] if form.cleaned_data['yearCarro'] is not None else "-"
        
        resultado['promoPublicidad'] = 50  # Assuming this is a fixed value
        resultado['transmision'] = form.cleaned_data['transmisionAuto'] if form.cleaned_data['transmisionAuto'] is not None else "-"
        resultado['nuevoAuto'] = form.cleaned_data['nuevoAuto'] if form.cleaned_data['nuevoAuto'] is not None else "-"
        resultado['kilometrajeAuto'] = form.cleaned_data['kilometrajeAuto'] if form.cleaned_data['kilometrajeAuto'] is not None else 0
        resultado['observaciones'] = form.cleaned_data['observaciones'] if form.cleaned_data['observaciones'] is not None else "-"

        #Datos del deudor
        resultado['tiempoServicio'] = form.cleaned_data['tiempoServicio'] if form.cleaned_data['tiempoServicio'] is not None else "-"
        resultado['ingresos'] = form.cleaned_data['ingresos'] if form.cleaned_data['ingresos'] is not None else "-"
        resultado['nombreEmpresa'] = form.cleaned_data['nombreEmpresa'] if form.cleaned_data['nombreEmpresa'] is not None else "-"
        resultado['referenciasAPC'] = form.cleaned_data['referenciasAPC'] if form.cleaned_data['referenciasAPC'] is not None else "-"
        resultado['cartera'] = form.cleaned_data['cartera'] if form.cleaned_data['cartera'] is not None else "-"
        resultado['licencia'] = form.cleaned_data['licencia'] if form.cleaned_data['licencia'] is not None else "-"
        resultado['posicion'] = form.cleaned_data['posicion'] if form.cleaned_data['posicion'] is not None else "-"
        resultado['perfilUniversitario'] = form.cleaned_data['perfilUniversitario'] if form.cleaned_data['perfilUniversitario'] is not None else "-"

        #DATOS NIVEL DE ENDEUDAMIENTO
        resultado['salarioBaseMensual'] = form.cleaned_data['salarioBaseMensual'] if form.cleaned_data['salarioBaseMensual'] is not None else 0
        resultado['horasExtrasMonto'] = form.cleaned_data['horasExtrasMonto'] if form.cleaned_data['horasExtrasMonto'] is not None else 0
        resultado['horasExtrasDcto'] = form.cleaned_data['horasExtrasDcto'] if form.cleaned_data['horasExtrasDcto'] is not None else 0
        resultado['primaMonto'] = form.cleaned_data['primaMonto'] if form.cleaned_data['primaMonto'] is not None else 0
        resultado['primaDcto'] = form.cleaned_data['primaDcto'] if form.cleaned_data['primaDcto'] is not None else 0
        resultado['bonosMonto'] = form.cleaned_data['bonosMonto'] if form.cleaned_data['bonosMonto'] is not None else 0
        resultado['bonosDcto'] = form.cleaned_data['bonosDcto'] if form.cleaned_data['bonosDcto'] is not None else 0
        resultado['otrosMonto'] = form.cleaned_data['otrosMonto'] if form.cleaned_data['otrosMonto'] is not None else 0
        resultado['otrosDcto'] = form.cleaned_data['otrosDcto'] if form.cleaned_data['otrosDcto'] is not None else 0

        #DESCUENTO DIRECTO
        resultado['siacapMonto'] = form.cleaned_data['siacapMonto'] if form.cleaned_data['siacapMonto'] is not None else 0
        resultado['siacapDcto'] = form.cleaned_data['siacapDcto'] if form.cleaned_data['siacapDcto'] is not None else False
        resultado['praaMonto'] = form.cleaned_data['praaMonto'] if form.cleaned_data['praaMonto'] is not None else 0
        resultado['praaDcto'] = form.cleaned_data['praaDcto'] if form.cleaned_data['praaDcto'] is not None else False
        resultado['dirOtrosMonto1'] = form.cleaned_data['dirOtrosMonto1'] if form.cleaned_data['dirOtrosMonto1'] is not None else 0
        resultado['dirOtros1'] = form.cleaned_data['dirOtros1'] if form.cleaned_data['dirOtros1'] is not None else "-"
        resultado['dirOtrosDcto1'] = form.cleaned_data['dirOtrosDcto1'] if form.cleaned_data['dirOtrosDcto1'] is not None else False
        resultado['dirOtrosMonto2'] = form.cleaned_data['dirOtrosMonto2'] if form.cleaned_data['dirOtrosMonto2'] is not None else 0
        resultado['dirOtros2'] = form.cleaned_data['dirOtros2'] if form.cleaned_data['dirOtros2'] is not None else "-"
        resultado['dirOtrosDcto2'] = form.cleaned_data['dirOtrosDcto2'] if form.cleaned_data['dirOtrosDcto2'] is not None else False
        resultado['dirOtrosMonto3'] = form.cleaned_data['dirOtrosMonto3'] if form.cleaned_data['dirOtrosMonto3'] is not None else 0
        resultado['dirOtros3'] = form.cleaned_data['dirOtros3'] if form.cleaned_data['dirOtros3'] is not None else "-"
        resultado['dirOtrosDcto3'] = form.cleaned_data['dirOtrosDcto3'] if form.cleaned_data['dirOtrosDcto3'] is not None else False
        resultado['dirOtrosMonto4'] = form.cleaned_data['dirOtrosMonto4'] if form.cleaned_data['dirOtrosMonto4'] is not None else 0
        resultado['dirOtros4'] = form.cleaned_data['dirOtros4'] if form.cleaned_data['dirOtros4'] is not None else "-"
        resultado['dirOtrosDcto4'] = form.cleaned_data['dirOtrosDcto4'] if form.cleaned_data['dirOtrosDcto4'] is not None else False


        #PAGO VOLUNTARIO
        resultado['pagoVoluntario1'] = form.cleaned_data['pagoVoluntario1'] if form.cleaned_data['pagoVoluntario1'] is not None else 0
        resultado['pagoVoluntarioMonto1'] = form.cleaned_data['pagoVoluntarioMonto1'] if form.cleaned_data['pagoVoluntarioMonto1'] is not None else 0
        resultado['pagoVoluntarioDcto1'] = form.cleaned_data['pagoVoluntarioDcto1'] if form.cleaned_data['pagoVoluntarioDcto1'] is not None else 0
        resultado['pagoVoluntario2'] = form.cleaned_data['pagoVoluntario2'] if form.cleaned_data['pagoVoluntario2'] is not None else 0
        resultado['pagoVoluntarioMonto2'] = form.cleaned_data['pagoVoluntarioMonto2'] if form.cleaned_data['pagoVoluntarioMonto2'] is not None else 0
        resultado['pagoVoluntarioDcto2'] = form.cleaned_data['pagoVoluntarioDcto2'] if form.cleaned_data['pagoVoluntarioDcto2'] is not None else 0
        resultado['pagoVoluntario3'] = form.cleaned_data['pagoVoluntario3'] if form.cleaned_data['pagoVoluntario3'] is not None else 0
        resultado['pagoVoluntarioMonto3'] = form.cleaned_data['pagoVoluntarioMonto3'] if form.cleaned_data['pagoVoluntarioMonto3'] is not None else 0
        resultado['pagoVoluntarioDcto3'] = form.cleaned_data['pagoVoluntarioDcto3'] if form.cleaned_data['pagoVoluntarioDcto3'] is not None else 0
        resultado['pagoVoluntario4'] = form.cleaned_data['pagoVoluntario4'] if form.cleaned_data['pagoVoluntario4'] is not None else 0
        resultado['pagoVoluntarioMonto4'] = form.cleaned_data['pagoVoluntarioMonto4'] if form.cleaned_data['pagoVoluntarioMonto4'] is not None else 0
        resultado['pagoVoluntarioDcto4'] = form.cleaned_data['pagoVoluntarioDcto4'] if form.cleaned_data['pagoVoluntarioDcto4'] is not None else 0
        resultado['pagoVoluntario5'] = form.cleaned_data['pagoVoluntario5'] if form.cleaned_data['pagoVoluntario5'] is not None else 0
        resultado['pagoVoluntarioMonto5'] = form.cleaned_data['pagoVoluntarioMonto5'] if form.cleaned_data['pagoVoluntarioMonto5'] is not None else 0
        resultado['pagoVoluntarioDcto5'] = form.cleaned_data['pagoVoluntarioDcto5'] if form.cleaned_data['pagoVoluntarioDcto5'] is not None else 0
        resultado['pagoVoluntario6'] = form.cleaned_data['pagoVoluntario6'] if form.cleaned_data['pagoVoluntario6'] is not None else 0
        resultado['pagoVoluntarioMonto6'] = form.cleaned_data['pagoVoluntarioMonto6'] if form.cleaned_data['pagoVoluntarioMonto6'] is not None else 0
        resultado['pagoVoluntarioDcto6'] = form.cleaned_data['pagoVoluntarioDcto6'] if form.cleaned_data['pagoVoluntarioDcto6'] is not None else 0
        
        resultado['horasExtrasMonto'] = form.cleaned_data['horasExtrasMonto'] if form.cleaned_data['horasExtrasMonto'] is not None else 0  
        #PRORRATEO
        resultado['mes0'] = form.cleaned_data['mes0'] if form.cleaned_data['mes0'] is not None else ""
        resultado['mes1'] = form.cleaned_data['mes1'] if form.cleaned_data['mes1'] is not None else ""
        resultado['mes2'] = form.cleaned_data['mes2'] if form.cleaned_data['mes2'] is not None else ""
        resultado['mes3'] = form.cleaned_data['mes3'] if form.cleaned_data['mes3'] is not None else ""
        resultado['mes4'] = form.cleaned_data['mes4'] if form.cleaned_data['mes4'] is not None else ""
        resultado['mes5'] = form.cleaned_data['mes5'] if form.cleaned_data['mes5'] is not None else ""
        resultado['mes6'] = form.cleaned_data['mes6'] if form.cleaned_data['mes6'] is not None else ""
        resultado['mes7'] = form.cleaned_data['mes7'] if form.cleaned_data['mes7'] is not None else ""
        resultado['mes8'] = form.cleaned_data['mes8'] if form.cleaned_data['mes8'] is not None else ""
        resultado['mes9'] = form.cleaned_data['mes9'] if form.cleaned_data['mes9'] is not None else ""
        resultado['mes10'] = form.cleaned_data['mes10'] if form.cleaned_data['mes10'] is not None else ""
        resultado['mes11'] = form.cleaned_data['mes11'] if form.cleaned_data['mes11'] is not None else ""
        resultado['primerMes'] = form.cleaned_data['primerMes'] if form.cleaned_data['primerMes'] is not None else ""
        resultado['tipoProrrateo'] = form.cleaned_data['tipoProrrateo'] if form.cleaned_data['tipoProrrateo'] is not None else ""
        #print('primer mes', resultado['primerMes'],form.cleaned_data['primerMes'])
        
        # MONTO LETRA SIN SEGUROS
        resultado['wrkLetraSinSeguros'] = resultado['wrkMontoLetra']  - resultado['wrkLetraSeguro']
        resultado['wrkLetraSinSeguros'] = round(resultado['wrkLetraSinSeguros'], 2)
        resultado['wrkLetraConSeguros'] = round(resultado['wrkMontoLetra'], 2)
        

        resultado['calcComiCierreFinal'] = round(resultado['calcComiCierreFinal'], 2)
       
        resultado['cashback'] = form.cleaned_data['cashback'] if form.cleaned_data['cashback'] is not None else 0
        resultado['cashback'] = round(resultado['cashback'], 2)
        resultado['r1']=round(resultado['r1'],2)
        resultado['abono'] = form.cleaned_data['abono'] if form.cleaned_data['abono'] is not None else 0
        resultado['abono'] = round(resultado['abono'], 2)
        resultado['abonoPorcentaje'] = form.cleaned_data['abonoPorcentaje'] if form.cleaned_data['abonoPorcentaje'] is not None else 0
        resultado['abonoPorcentaje'] = round(resultado['abonoPorcentaje'], 2)
        #print('abonoporcentaje', resultado['abonoPorcentaje'])

        resultado['movOpcion'] = form.cleaned_data['movOpcion'] if form.cleaned_data['movOpcion'] is not None else 0
        resultado['averageIngresos'] = form.cleaned_data['averageIngresos'] if form.cleaned_data['averageIngresos'] is not None else 0

    except Exception as e:
        print(f"Error: {e} at line {sys.exc_info()[-1].tb_lineno}")
    
        # Convert Decimal fields to floats
        # Convert Decimal fields to floats
    from ..views import convert_decimal_to_float
    resultado = convert_decimal_to_float(resultado)
    from ..views import nivelEndeudamiento

    #CALCULO NIVEL DE ENDEUDAMIENTO - REAL
    print("-----Nivel Endeudamiento-----")
    resultadoNivel = nivelEndeudamiento(resultado)
    resultado['salarioNeto'] = resultadoNivel['salarioNeto']
    resultado['porSalarioNeto'] = resultadoNivel['porSalarioNeto']
    resultado['salarioNetoActual'] = resultadoNivel['salarioNetoActual']
    resultado['totalIngresosAdicionales'] = resultadoNivel['totalIngresosAdicionales']
    resultado['totalIngresosMensuales'] = resultadoNivel['totalIngresosMensuales']
    resultado['totalDescuentoDirecto'] = resultadoNivel['totalDescuentoDirecto']
    resultado['totalPagoVoluntario'] = resultadoNivel['totalPagoVoluntario']
    resultado['totalDescuentosLegales'] = resultadoNivel['totalDescuentosLegales']
    #nivel de endeudamiento - completo
    resultado['totalIngresosMensualesCompleto'] = resultadoNivel['totalIngresosMensualesCompleto']
    resultado['totalDescuentosLegalesCompleto'] = resultadoNivel['totalDescuentosLegalesCompleto']
    resultado['salarioNetoActualCompleto'] = resultadoNivel['salarioNetoActualCompleto']
    resultado['salarioNetoCompleto'] = resultadoNivel['salarioNetoCompleto']
    resultado['porSalarioNetoCompleto'] = resultadoNivel['porSalarioNetoCompleto']
    # Perform the calculation logic here
    # ...
    print("-----Nivel Endeudamiento FIn-----")
    
    return resultado, iteration_data

