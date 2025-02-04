from decimal import Decimal
import pprint
import datetime
from ..fideicomiso.fideicomiso import generarFideicomiso3
from ..views import nivelEndeudamiento



def convert_decimal_to_float(data):
    
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
            
    return data


def set_calculated_values2(new_instance, resultado, aseguradora,form, codeudorResultado, resultadoNivelCodeudor):

    new_instance.wrkMontoLetra = resultado['wrkMontoLetra']
    new_instance.montoManejoT = resultado['montoManejoT']
    new_instance.monto_manejo_b = resultado['montoManejoB']
    new_instance.tasaEstimada = resultado['tasaEstimada']
    new_instance.r1 = resultado['r1']
    new_instance.auxMonto2 = resultado['auxMonto2']
    new_instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
    new_instance.calcMontoNotaria = resultado['calcMontoNotaria']
    new_instance.calcMontoTimbres = resultado['calcMontoTimbres']
    new_instance.tablaTotalPagos = resultado['tablaTotalPagos']
    new_instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
    new_instance.tablaTotalFeci = resultado['tablaTotalFeci']
    new_instance.tablaTotalInteres = resultado['tablaTotalInteres']
    new_instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
    new_instance.manejo_5porc = resultado['manejo_5porc']
    new_instance.valorAuto = resultado['valorAuto']
    new_instance.aseguradora = aseguradora
    new_instance.siacapMonto = resultado['siacapMonto']
    new_instance.siacapDcto = resultado['siacapDcto']
    new_instance.praaMonto = resultado['praaMonto']
    new_instance.praaDcto = resultado['praaDcto']
    new_instance.wrkLetraSinSeguros = resultado['wrkLetraSinSeguros']
    new_instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
    new_instance.tasaBruta = resultado['tasaBruta']
    #resultado nivel de endeuamiento - real
    new_instance.salarioBaseMensual = resultado['salarioBaseMensual']
    new_instance.totalDescuentosLegales = resultado['totalDescuentosLegales']
    new_instance.totalDescuentoDirecto = resultado['totalDescuentoDirecto']
    new_instance.totalPagoVoluntario = resultado['totalPagoVoluntario']
    new_instance.salarioNetoActual = resultado['salarioNetoActual']
    new_instance.salarioNeto = resultado['salarioNeto']
    new_instance.porSalarioNeto = resultado['porSalarioNeto']
    new_instance.totalIngresosAdicionales = resultado['totalIngresosAdicionales']
    new_instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
    new_instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
    new_instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
    new_instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
    new_instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']
    #resultado codeudor nivel de endeudamiento
    if form.cleaned_data['aplicaCodeudor'] == "si":
        new_instance.cosalarioBaseMensual = codeudorResultado['salarioBaseMensual']
        new_instance.cototalDescuentosLegales = resultadoNivelCodeudor['totalDescuentosLegales']
        new_instance.cototalDescuentoDirecto = resultadoNivelCodeudor['totalDescuentoDirecto']
        new_instance.cototalPagoVoluntario = resultadoNivelCodeudor['totalPagoVoluntario']
        new_instance.cosalarioNetoActual = resultadoNivelCodeudor['salarioNetoActual']
        new_instance.cosalarioNeto = resultadoNivelCodeudor['salarioNeto']
        new_instance.coporSalarioNeto = resultadoNivelCodeudor['porSalarioNeto']
        new_instance.cototalIngresosAdicionales = resultadoNivelCodeudor['totalIngresosAdicionales']
        new_instance.cototalIngresosMensualesCompleto = resultadoNivelCodeudor['totalIngresosMensualesCompleto']
        new_instance.cototalDescuentosLegalesCompleto = resultadoNivelCodeudor['totalDescuentosLegalesCompleto']
        new_instance.cosalarioNetoActualCompleto = resultadoNivelCodeudor['salarioNetoActualCompleto']
        new_instance.cosalarioNetoCompleto = resultadoNivelCodeudor['salarioNetoCompleto']
        new_instance.coporSalarioNetoCompleto = resultadoNivelCodeudor['porSalarioNetoCompleto']
    #-------          
    return new_instance

def set_calculated_values(new_form, resultado, aseguradora):


    new_form.instance.tasaEstimada = resultado['tasaEstimada']
    new_form.instance.tasaBruta = resultado['tasaBruta']
    new_form.instance.r1 = resultado['r1']
    new_form.instance.auxMonto2 = resultado['auxMonto2']
    new_form.instance.wrkMontoLetra = resultado['wrkMontoLetra']
    new_form.instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
    new_form.instance.wrkLetraSinSeguros = resultado['wrkLetraSinSeguros']
    new_form.instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
    new_form.instance.calcMontoNotaria = resultado['calcMontoNotaria']
    new_form.instance.calcMontoTimbres = resultado['calcMontoTimbres']
    new_form.instance.tablaTotalPagos = resultado['tablaTotalPagos']
    new_form.instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
    new_form.instance.tablaTotalFeci = resultado['tablaTotalFeci']
    new_form.instance.tablaTotalInteres = resultado['tablaTotalInteres']
    new_form.instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
    new_form.instance.manejo_5porc = resultado['manejo_5porc']
    new_form.instance.valorAuto = resultado['valorAuto']
    new_form.instance.aseguradora = aseguradora
    new_form.instance.siacapMonto = resultado['siacapMonto']
    new_form.instance.siacapDcto = resultado['siacapDcto']
    new_form.instance.praaMonto = resultado['praaMonto']
    new_form.instance.praaDcto = resultado['praaDcto']
    #resultado nivel de endeuamiento - real
    new_form.instance.salarioBaseMensual = resultado['salarioBaseMensual']
    new_form.instance.totalDescuentosLegales = resultado['totalDescuentosLegales']
    new_form.instance.totalDescuentoDirecto = resultado['totalDescuentoDirecto']
    new_form.instance.totalPagoVoluntario = resultado['totalPagoVoluntario']
    new_form.instance.salarioNetoActual = resultado['salarioNetoActual']
    new_form.instance.salarioNeto = resultado['salarioNeto']
    new_form.instance.porSalarioNeto = resultado['porSalarioNeto']
    new_form.instance.totalIngresosAdicionales = resultado['totalIngresosAdicionales']
    new_form.instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
    new_form.instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
    new_form.instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
    new_form.instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
    new_form.instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']

    return new_form


def aplicaCodeudor(form, resultado, new_form):

    codeudorResultado = {
                        'primaMonto': form.cleaned_data['coprimaMonto'],
                        'bonosMonto': form.cleaned_data['cobonosMonto'],
                        'otrosMonto': form.cleaned_data['cootrosMonto'],
                        'horasExtrasMonto': form.cleaned_data['cohorasExtrasMonto'],
                        'siacapMonto': form.cleaned_data['cosiacapMonto'],
                        'praaMonto': form.cleaned_data['copraaMonto'],
                        'dirOtrosMonto1': form.cleaned_data['codirOtrosMonto1'],
                        'dirOtrosMonto2': form.cleaned_data['codirOtrosMonto2'],
                        'dirOtrosMonto3': form.cleaned_data['codirOtrosMonto3'],
                        'dirOtrosMonto4': form.cleaned_data['codirOtrosMonto4'],
                        'pagoVoluntarioMonto1' : form.cleaned_data['copagoVoluntarioMonto1'],
                        'pagoVoluntarioMonto2' : form.cleaned_data['copagoVoluntarioMonto2'],
                        'pagoVoluntarioMonto3' : form.cleaned_data['copagoVoluntarioMonto3'],
                        'pagoVoluntarioMonto4' : form.cleaned_data['copagoVoluntarioMonto4'],
                        'pagoVoluntarioMonto5' : form.cleaned_data['copagoVoluntarioMonto5'],
                        'pagoVoluntarioMonto6' : form.cleaned_data['copagoVoluntarioMonto6'],
                        'salarioBaseMensual' : form.cleaned_data['codeudorIngresos'],
                        'cartera' : form.cleaned_data['codeudorCartera'],
                        'wrkLetraConSeguros' : resultado['wrkLetraConSeguros'],

                    }

    codeudorResultado = convert_decimal_to_float(codeudorResultado)
    #print('iniciar nivel codeudor')
    resultadoNivelCodeudor = nivelEndeudamiento(codeudorResultado)
    #print('resultadoNivelCodeudor', resultadoNivelCodeudor)
    new_form.instance.cosalarioBaseMensual = codeudorResultado['salarioBaseMensual']
    new_form.instance.cototalDescuentosLegales = resultadoNivelCodeudor['totalDescuentosLegales']
    new_form.instance.cototalDescuentoDirecto = resultadoNivelCodeudor['totalDescuentoDirecto']
    new_form.instance.cototalPagoVoluntario = resultadoNivelCodeudor['totalPagoVoluntario']
    new_form.instance.cosalarioNetoActual = resultadoNivelCodeudor['salarioNetoActual']
    new_form.instance.cosalarioNeto = resultadoNivelCodeudor['salarioNeto']
    new_form.instance.coporSalarioNeto = resultadoNivelCodeudor['porSalarioNeto']
    new_form.instance.cototalIngresosAdicionales = resultadoNivelCodeudor['totalIngresosAdicionales']
    new_form.instance.cototalIngresosMensualesCompleto = resultadoNivelCodeudor['totalIngresosMensualesCompleto']
    new_form.instance.cototalDescuentosLegalesCompleto = resultadoNivelCodeudor['totalDescuentosLegalesCompleto']
    new_form.instance.cosalarioNetoActualCompleto = resultadoNivelCodeudor['salarioNetoActualCompleto']
    new_form.instance.cosalarioNetoCompleto = resultadoNivelCodeudor['salarioNetoCompleto']
    new_form.instance.coporSalarioNetoCompleto = resultadoNivelCodeudor['porSalarioNetoCompleto']

    return new_form, codeudorResultado, resultadoNivelCodeudor
    


def prepResultado(cotizacion):

    resultado = {
        'auxMonto2': cotizacion.auxMonto2,
        'numero_cotizacion': cotizacion.NumeroCotizacion,
        'r1': cotizacion.r1,
        'tasaEstimada': cotizacion.tasaEstimada,
        'calcComiCierreFinal': cotizacion.calcComiCierreFinal,
        'auxPlazoPago': cotizacion.plazoPago,
        'wrkLetraSinSeguros': cotizacion.wrkLetraSinSeguros,
        'wrkLetraSeguro': cotizacion.wrkLetraSeguro,
        'wrkMontoLetra': cotizacion.wrkMontoLetra,
        'montoMensualSeguro': cotizacion.montoMensualSeguro,
        'wrkLetraConSeguros': cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro,
        'tablaTotalPagos': cotizacion.tablaTotalPagos,
        'nombreCliente': cotizacion.nombreCliente,
        'valorAuto': cotizacion.valorAuto,
        'abono': cotizacion.abono,
        'salarioBaseMensual': cotizacion.salarioBaseMensual,
        'totalDescuentosLegales': cotizacion.totalDescuentosLegales,
        'totalDescuentoDirecto': cotizacion.totalDescuentoDirecto,
        'totalPagoVoluntario': cotizacion.totalPagoVoluntario,
        'salarioNetoActual': cotizacion.salarioNetoActual,
        'salarioNeto': cotizacion.salarioNeto,
        'porSalarioNeto': cotizacion.porSalarioNeto,
        'totalIngresosAdicionales': cotizacion.totalIngresosAdicionales,
        'totalIngresosMensualesCompleto': cotizacion.totalIngresosMensualesCompleto,
        'totalDescuentosLegalesCompleto': cotizacion.totalDescuentosLegalesCompleto,
        'salarioNetoActualCompleto': cotizacion.salarioNetoActualCompleto,
        'salarioNetoCompleto': cotizacion.salarioNetoCompleto,
        'porSalarioNetoCompleto': cotizacion.porSalarioNetoCompleto,
        'cosalarioBaseMensual': cotizacion.cosalarioBaseMensual,
        'cototalDescuentosLegales': cotizacion.cototalDescuentosLegales,
        'cototalDescuentoDirecto': cotizacion.cototalDescuentoDirecto,
        'cototalPagoVoluntario': cotizacion.cototalPagoVoluntario,
        'cosalarioNetoActual': cotizacion.cosalarioNetoActual,
        'cosalarioNeto': cotizacion.cosalarioNeto,
        'coporSalarioNeto': cotizacion.coporSalarioNeto,
        'cototalIngresosAdicionales': cotizacion.cototalIngresosAdicionales,
        'cototalIngresosMensualesCompleto': cotizacion.cototalIngresosMensualesCompleto,
        'cototalDescuentosLegalesCompleto': cotizacion.cototalDescuentosLegalesCompleto,
        'cosalarioNetoActualCompleto': cotizacion.cosalarioNetoActualCompleto,
        'cosalarioNetoCompleto': cotizacion.cosalarioNetoCompleto,
        'coporSalarioNetoCompleto': cotizacion.coporSalarioNetoCompleto,
        'porcentajeLetraSeguro': round(((cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro) / cotizacion.salarioBaseMensual * 100), 2) if cotizacion.salarioBaseMensual not in [None, 0] else 0,
        'coporcentajeLetraSeguro': round(((cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro) / cotizacion.cosalarioBaseMensual * 100), 2) if cotizacion.cosalarioBaseMensual not in [None, 0] else 0,
        'porcentajeLetraSeguroCompleto': round(((cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro)/cotizacion.totalIngresosMensualesCompleto * 100),2) if cotizacion.totalIngresosMensualesCompleto not in [None, 0] else 0,
        'coporcentajeLetraSeguroCompleto': round(((cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro)/cotizacion.cototalIngresosMensualesCompleto * 100),2) if cotizacion.cototalIngresosMensualesCompleto not in [None, 0] else 0,
        'familiarSalarioBaseMensual': (cotizacion.salarioNetoActual or 0) + (cotizacion.cosalarioNetoActual or 0),
        'familiarSalarioNeto': ((cotizacion.salarioNetoActual or 0) + (cotizacion.cosalarioNetoActual or 0)) - ((cotizacion.wrkMontoLetra or 0) + (cotizacion.montoMensualSeguro or 0)),
    }


    try:
        familiarSalarioBaseMensual = resultado['familiarSalarioBaseMensual'] or 0
        salarioBaseMensual = cotizacion.salarioBaseMensual or 0
        cosalarioBaseMensual = cotizacion.cosalarioBaseMensual or 0
        familiarSalarioNeto = resultado['familiarSalarioNeto'] or 0
        familiarNetoActualCompleto = cotizacion.salarioNetoActualCompleto or 0
        cosalarioNetoActualCompleto = cotizacion.cosalarioNetoActualCompleto or 0
        wrkMontoLetra = cotizacion.wrkMontoLetra or 0
        montoMensualSeguro = cotizacion.montoMensualSeguro or 0
        totalIngresosMensualesCompleto = cotizacion.totalIngresosMensualesCompleto or 0
        cototalIngresosMensualesCompleto = cotizacion.cototalIngresosMensualesCompleto or 0

        resultado['familiarporNetoActual'] = round(familiarSalarioBaseMensual / (salarioBaseMensual + cosalarioBaseMensual) * 100, 2) if (salarioBaseMensual + cosalarioBaseMensual) != 0 else 0
        resultado['familiarpoSalarioNeto'] = round(familiarSalarioNeto / (salarioBaseMensual + cosalarioBaseMensual) * 100, 2) if (salarioBaseMensual + cosalarioBaseMensual) != 0 else 0
        resultado['familiarNetoActualCompleto'] = round(familiarNetoActualCompleto + cosalarioNetoActualCompleto, 2)
        resultado['familiarporNetoActualCompleto'] = round(resultado['familiarNetoActualCompleto'] / cosalarioBaseMensual * 100, 2) if cosalarioBaseMensual != 0 else 0
        resultado['familiarSalarioNetoCompleto'] = resultado['familiarNetoActualCompleto'] - (wrkMontoLetra + montoMensualSeguro)
        resultado['familiarporSalarioNeto'] = round(resultado['familiarSalarioNetoCompleto'] / (totalIngresosMensualesCompleto + cototalIngresosMensualesCompleto) * 100, 2) if (totalIngresosMensualesCompleto + cototalIngresosMensualesCompleto) != 0 else 0
        
    except ZeroDivisionError:
        resultado['familiarporNetoActual'] = 0
        resultado['familiarpoSalarioNeto'] = 0
        resultado['familiarNetoActualCompleto'] = 0
        resultado['familiarporNetoActualCompleto'] = 0
        resultado['familiarSalarioNetoCompleto'] = 0
        resultado['familiarporSalarioNeto'] = 0
    return resultado



def perform_fideicomiso_calculation(form):
    # Extract form data
  # Extract form data
    edad = form.cleaned_data['edad']
    sexo = form.cleaned_data['sexo']
    jubilado = form.cleaned_data['jubilado']
    nombreCliente = form.cleaned_data['nombreCliente']
    cotMontoPrestamo = Decimal(form.cleaned_data['montoPrestamo'])
    calcTasaInteres = 10 / 100
    calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
    auxPlazoPago = form.cleaned_data['plazoPago']
    patrono = form.cleaned_data['patronoCodigo'] if form.cleaned_data['patronoCodigo'] is not None else 9999
    sucursal = 13
    auxPeriocidad = 1
    forma_pago = 4
    #COLECTIVO DE CREDITO
    aseguradora = form.cleaned_data['aseguradora']
    #print('aseguradora', aseguradora)
    codigoSeguro = aseguradora.codigo
    r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
    comisionVendedor = form.cleaned_data['vendedorComision']
    #CAMPOS SEGURO AUTO
    financiaSeguro = form.cleaned_data['financiaSeguro']
    mesesFinanciaSeguro = form.cleaned_data['mesesFinanciaSeguro']
    montoanualSeguro = form.cleaned_data['montoanualSeguro']
    montoMensualSeguro = form.cleaned_data['montoMensualSeguro']
    cantPagosSeguro = form.cleaned_data['cantPagosSeguro']
    sucursal = form.cleaned_data['sucursal']
    montoLetraSeguroAdelantado = mesesFinanciaSeguro * montoMensualSeguro
    montoLetraSeguroAdelantado = round(montoLetraSeguroAdelantado, 2)
    if montoLetraSeguroAdelantado is None:
        montoLetraSeguroAdelantado = 0
        

    
    #parse cotMontoPRestamo to float
    cotMontoPrestamo = float(cotMontoPrestamo)
    calcTasaInteres = float(calcTasaInteres)
    calcComiCierre = float(calcComiCierre)
    r_deseada = float(r_deseada)
    comisionVendedor = float(comisionVendedor)
    montoanualSeguro = float(montoanualSeguro)
    montoMensualSeguro = float(montoMensualSeguro)
    sucursal = int(sucursal)
    #print('Sucursal', sucursal)
    # Call the generarFideicomiso2 function
    params = {
        'edad': edad,
        'sucursal': sucursal,
        'sexo': sexo,
        'jubilado': jubilado,
        'cotMontoPrestamo': cotMontoPrestamo,
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
        'financiaSeguro': financiaSeguro,
        'mesesFinanciaSeguro': mesesFinanciaSeguro,
        'montoanualSeguro': montoanualSeguro,
        'montoMensualSeguro': montoMensualSeguro,
        'cantPagosSeguro': cantPagosSeguro,
        'gastoFideicomiso': 291.90,

    }
    ##print('RESULTADO PARAMETROS', params)
    resultado = generarFideicomiso3(params)
    
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
    resultado['montoMensualSeguro'] = montoMensualSeguro if montoMensualSeguro is not None else 0
    resultado['montoanualSeguro'] = montoanualSeguro if montoanualSeguro is not None else 0
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
    resultado['wrkLetraConSeguros'] = resultado['wrkMontoLetra'] + resultado['montoMensualSeguro']
    resultado['wrkLetraConSeguros'] = round(resultado['wrkLetraConSeguros'], 2)
    resultado['calcComiCierreFinal'] = round(resultado['calcComiCierreFinal'], 2)
    resultado['montoLetraSeguroAdelantado'] =montoLetraSeguroAdelantado
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
    
        # Convert Decimal fields to floats
        # Convert Decimal fields to floats
    from ..views import convert_decimal_to_float
    resultado = convert_decimal_to_float(resultado)
    from ..views import nivelEndeudamiento
    #CALCULO NIVEL DE ENDEUDAMIENTO - REAL
    
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
    
    return resultado


def cotizacionDetail_backup(request, pk):
    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=pk)
    form = FideicomisoForm(instance=cotizacion)
    consulta = {
        'consulta': True,
    }

    resultado = prepResultado(cotizacion)
    context = {
        'form': form,
        'cotizacion': cotizacion,
        'resultado': resultado,
        'consulta': consulta,
    }

    # Check if cotizacion has any Documento associated
    documentos = CotizacionDocumento.objects.filter(cotizacion=cotizacion)
    context['documentos'] = documentos

    # check if user has the property in true pruebaFuncionalidades
    if request.user.userprofile.pruebaFuncionalidades:
        context['pruebaFuncionalidades'] = True
    

    if request.method == 'POST':
        form = FideicomisoForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            try:
                aseguradora = form.cleaned_data['aseguradora']
                resultado = perform_fideicomiso_calculation(form)

                # Update the existing form instance
                form = set_calculated_values(form, resultado, aseguradora)

                codeudorResultado = {}
                resultadoNivelCodeudor = {}

                if form.cleaned_data['aplicaCodeudor'] == "si":
                    new_form, codeudorResultado, resultadoNivelCodeudor = aplicaCodeudor(form, resultado, new_form)


                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                    instance = set_calculated_values2(instance, resultado, aseguradora, form, codeudorResultado, resultadoNivelCodeudor)
                    instance.save()

                    # Save document data
                    documentos_data = request.POST.get('documentos_data')
                    if documentos_data:
                        documentos = json.loads(documentos_data)
                        for doc in documentos:
                            try:
                                documento_file = request.FILES.get(doc['documento'])
                                CotizacionDocumento.objects.create(
                                    cotizacion=instance,
                                    tipo_documento=doc['tipoDocumento'],
                                    documento=documento_file,  # Reference the file correctly
                                    observaciones=doc['observaciones']
                                )
                                print("Documento guardado", doc['tipoDocumento'])
                            except Exception as e:
                                print(f"Error saving documento {doc['tipoDocumento']}: {e}")

                    return redirect('cotizacion_detail', pk=int(instance.NumeroCotizacion))
                else:
                    logger.warning("Form is not valid: %s", form.errors)
                    messages.error(request, 'An error occurred while updating the record.')
            except Exception as e:
                logger.error("Error in cotizacionDetail: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
        else:
            logger.warning("Form is not valid: %s", form.errors)
            messages.error(request, 'An error occurred while processing your request.')

    return render(request, 'fideicomiso_form.html', context)




def calculoInicial(resultado,form, sexo, montoMensualSeguro, montoanualSeguro, auxPlazoPago, montoLetraSeguroAdelantado, aseguradora):

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
    resultado['apcScore'] = form.cleaned_data['apcScore'] if form.cleaned_data['apcScore'] is not None else 0
    resultado['apcPI'] = form.cleaned_data['apcPI'] / 100 if form.cleaned_data['apcPI'] is not None else 0
    resultado['valorAuto'] = form.cleaned_data['valorAuto'] if form.cleaned_data['valorAuto'] is not None else 0
    resultado['cotPlazoPago'] = auxPlazoPago if auxPlazoPago is not None else 0
    resultado['vendedor'] = form.cleaned_data['vendedor'] if form.cleaned_data['vendedor'] is not None else "-"
    #DATOS DEL AUTO
    resultado['marcaAuto'] = form.cleaned_data['marca'] if form.cleaned_data['marca'] is not None else "-"
    resultado['lineaAuto'] = form.cleaned_data['modelo'] if form.cleaned_data['modelo'] is not None else "-"
    resultado['yearAuto'] = form.cleaned_data['yearCarro'] if form.cleaned_data['yearCarro'] is not None else "-"
    resultado['montoMensualSeguro'] = montoMensualSeguro if montoMensualSeguro is not None else 0
    resultado['montoanualSeguro'] = montoanualSeguro if montoanualSeguro is not None else 0
    resultado['promoPublicidad'] = 50  # Assuming this is a fixed value
    
    resultado['nuevoAuto'] = form.cleaned_data['nuevoAuto'] if form.cleaned_data['nuevoAuto'] is not None else "-"
    resultado['kilometrajeAuto'] = form.cleaned_data['kilometrajeAuto'] if form.cleaned_data['kilometrajeAuto'] is not None else 0
    resultado['observaciones'] = form.cleaned_data['observaciones'] if form.cleaned_data['observaciones'] is not None else "-"

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
    resultado['wrkLetraSinSeguros'] = resultado['wrkMontoLetra']  - resultado['wrkLetraSeguro']
    resultado['wrkLetraSinSeguros'] = round(resultado['wrkLetraSinSeguros'], 2)
    resultado['wrkLetraConSeguros'] = resultado['wrkMontoLetra'] + resultado['montoMensualSeguro']
    resultado['wrkLetraConSeguros'] = round(resultado['wrkLetraConSeguros'], 2)
    resultado['calcComiCierreFinal'] = round(resultado['calcComiCierreFinal'], 2)
    resultado['montoLetraSeguroAdelantado'] =montoLetraSeguroAdelantado
    resultado['cashback'] = form.cleaned_data['cashback'] if form.cleaned_data['cashback'] is not None else 0
    resultado['cashback'] = round(resultado['cashback'], 2)
    resultado['r1']=round(resultado['r1'],2)
    resultado['abono'] = form.cleaned_data['abono'] if form.cleaned_data['abono'] is not None else 0
    resultado['abono'] = round(resultado['abono'], 2)
    resultado['abonoPorcentaje'] = form.cleaned_data['abonoPorcentaje'] if form.cleaned_data['abonoPorcentaje'] is not None else 0
    resultado['abonoPorcentaje'] = round(resultado['abonoPorcentaje'], 2)
    #print('abonoporcentaje', resultado['abonoPorcentaje'])



    return resultado