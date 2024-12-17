import datetime

from .tablaAmortizacion import tablaAmortizacion
from .determinaMontoAmortizar import calculate_tasa_interes_mensual, determinar_monto_amortizar
from .calculoMensualidadSobresaldo import calculoMensualidadSobresaldo
from .rentabilidad import calculoRentabilidad
from .calculoVencimiento import  calculate_fecha_vencimiento
from .diasFECI import calculoDiasFECI
from .calculoSobresaldoEnCalculo import calculoSobresaldoEnCalculo
from .seguro import calculoSeguroTotal
from .notaria import search_gasto
from .fechaPromesaCK import calculoFechaPromesa
import logging
import datetime
from decimal import Decimal
import traceback

# Get an instance of a logger
logger = logging.getLogger(__name__)

def calculate_imc(weight, height):
    # Calculate IMC
    imc = weight / (height * height)
    
    # Define the ranges
    ranges = [
        { "min": 0, "max": 16, "description": "Delgadez Severa" },
        { "min": 16, "max": 16.99, "description": "Delgadez Moderada" },
        { "min": 17, "max": 18.49, "description": "Delgadez Aceptable" },
        { "min": 18.5, "max": 24.99, "description": "Peso Normal" },
        { "min": 25, "max": 29.99, "description": "Sobrepeso" },
        { "min": 30, "max": 34.99, "description": "Obeso: Tipo I" },
        { "min": 35, "max": 39.99, "description": "Obeso: Tipo II" },
        { "min": 40, "max": float('inf'), "description": "Obeso: Tipo III" }
    ]
    
    # Determine the description based on the IMC
    for range in ranges:
        if range["min"] <= imc <= range["max"]:
            return imc, range["description"]
    
    return imc, "Unknown"

def paga_diciembre(no_patrono, tipo_prestamo, forma_pago, cot_paga_diciembre):
        patrono_list = [5461, 640, 641, 642, 643, 649, 650, 651, 652, 653, 654]
        tipo_prestamo_list = ["LEASING", "CAR EXPRESS", "HIPOTECARIO", "FIDEICOMISO", "PREST AUTO"]
        forma_pago_list = [1, 6]
        
        if no_patrono in patrono_list or tipo_prestamo in tipo_prestamo_list or forma_pago in forma_pago_list or cot_paga_diciembre == "SI":
            return True
        return False

def calculate_plazo_maximo(sexo, edad_jub, year_nac, year_ini, month_nac, month_ini, day_nac, secuencia):
    # Calculate years to retirement
    ai = edad_jub
    bi = year_ini
    ci = year_nac

    di = ai - (bi - ci)
    if di < 0:
        di = 0

    years_para_jubilar = di

    # Calculate maximum term in months
    bi = month_nac
    d = day_nac
    ci = month_ini
    j = 0

    # Check if it is ACP
    if secuencia == 500:
        j = di * 11 + bi - ci - 3
    else:
        if d > 20:
            j = di * 11 + bi - ci
        else:
            j = di * 11 + bi - ci - 1

    return j

def identificar_notaria(sucursal, cantidad, tipo_prestamo, secuencia, patrono, referido):
    notaria = ""

    # Verificar sucursal
    if sucursal in [13, 4, 8, 24, 26]:
        if tipo_prestamo in ["PERSONAL", "CAR EXPRESS", "FIDEICOMISO", "PREST AUTO"]:
            if secuencia in [500, 400]:
                if referido == "SI":
                    notaria = 26
                else:
                    notaria = 2
            else:
                if referido in ["NO", ""]:
                    notaria = 2

    # SUCURSAL 2
    if sucursal == 2:
        if tipo_prestamo in ["PERSONAL", "CAR EXPRESS", "FIDEICOMISO", "PREST AUTO"]:
            if secuencia in [500, 400]:
                if referido == "SI":
                    notaria = 4
                else:
                    notaria = 3
            else:
                if referido in ["NO", ""]:
                    notaria = 3

    # SUCURSAL 11
    if sucursal == 11:
        if tipo_prestamo in ["PERSONAL", "CAR EXPRESS", "FIDEICOMISO", "PREST AUTO"]:
            if referido in ["NO", ""]:
                notaria = 11
            else:
                notaria = 26

    # SUCURSAL 7
    if sucursal == 7:
        if tipo_prestamo in ["PERSONAL", "CAR EXPRESS", "FIDEICOMISO", "PREST AUTO"]:
            if referido in ["NO", ""]:
                notaria = 10
            else:
                notaria = 26

    # LEASING or FIDEICOMISO
    if tipo_prestamo in ["LEASING", "FIDEICOMISO"]:
        if sucursal in [13, 4, 8, 2, 7, 11, 24, 26]:
            notaria = 46
            if cantidad <= 29999.99:
                notaria = 46
            elif 30000.00 <= cantidad <= 39999.99:
                notaria = 51
            elif 40000.00 <= cantidad <= 49999.99:
                notaria = 52
            elif cantidad >= 50000.00:
                notaria = 53

    # Patrono
    if patrono in [650, 643]:
        notaria = 18

    return notaria

def calculate_fecha_promesa_ck(no_patrono, diasprom1, diasprom2, fecha_calculo, from_date, until_date):
    # Ensure fecha_calculo is a datetime object
    if isinstance(fecha_calculo, str):
        fecha_calculo = datetime.datetime.strptime(fecha_calculo, "%Y-%m-%d")
    
   
    # Determine the value of ii based on no_patrono
    if 638 <= no_patrono <= 654 and no_patrono != 646:
        ii = diasprom2
    else:
        ii = diasprom1

    # Add 4 days if no_patrono is 620
    if no_patrono == 620:
        ii += 4

    habil_days_added = 0  # Counter for added "HABIL" days
    non_habil_days = 0  # Counter for non-HABIL days to track adjustments
    aux_libres = 0

    # Convert fecha_calculo to a datetime object
    #fecha_calculo = datetime.datetime.strptime(fecha_calculo, "%Y-%m-%d")
    from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    until_date = datetime.datetime.strptime(until_date, "%Y-%m-%d")

    # Generate the date range with "HABIL" and "NON-HABIL" days
    data_range = []
    current_date = from_date
    while current_date <= until_date:
        if current_date.weekday() == 6:  # Sunday
            data_range.append([current_date.strftime("%Y-%m-%d"), "NON-HABIL"])
        else:
            data_range.append([current_date.strftime("%Y-%m-%d"), "HABIL"])
        current_date += datetime.timedelta(days=1)

    # Function to get the type of day from data_range
    def get_tipo_dia(fecha):
        for row in data_range:
            if row[0] == fecha.strftime("%Y-%m-%d"):
                return row[1]
        return "NON-HABIL"

    # Loop to add grace days
    for i in range(1, ii):
        tipo_dia = get_tipo_dia(fecha_calculo)
        if tipo_dia != "HABIL":
            fecha_calculo += datetime.timedelta(days=1)
            aux_libres += 1
        fecha_calculo += datetime.timedelta(days=1)

    # Verify when it ends
    tipo_dia = get_tipo_dia(fecha_calculo)
    if tipo_dia != "HABIL":
        fecha_calculo += datetime.timedelta(days=1)
        aux_libres += 1
    
    #return fecha_calculo and add 1 day
    #print('Fecha Promesa: ',fecha_calculo)
    fecha_calculo=fecha_calculo + datetime.timedelta(days=1)
    #print('Fecha Promesa: ',fecha_calculo)
    return fecha_calculo.strftime("%Y-%m-%d")
    


def calculate_primer_dia_habil(fecha, from_date, until_date):
    # Set the first day of the month
    fecha_primer_dia = datetime.datetime(fecha.year, fecha.month, 1)

    # Convert from_date and until_date to datetime objects
    from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    until_date = datetime.datetime.strptime(until_date, "%Y-%m-%d")

    # Generate the date range with "HABIL" and "NON-HABIL" days
    data_range = []
    current_date = from_date
    while current_date <= until_date:
        if current_date.weekday() == 6:  # Sunday
            data_range.append([current_date.strftime("%Y-%m-%d"), "NON-HABIL"])
        else:
            data_range.append([current_date.strftime("%Y-%m-%d"), "HABIL"])
        current_date += datetime.timedelta(days=1)

    # Function to get the type of day from data_range
    def get_tipo_dia(fecha):
        for row in data_range:
            if row[0] == fecha.strftime("%Y-%m-%d"):
                return row[1]
        return "NON-HABIL"

    # Get the type of the first day
    temp_tipo_dia = get_tipo_dia(fecha_primer_dia)

    # Check if the first day is "HABIL"
    if temp_tipo_dia == "HABIL":
        return fecha_primer_dia.strftime("%Y-%m-%d")
    else:
        # Loop until a "HABIL" day is found
        while temp_tipo_dia != "HABIL":
            fecha_primer_dia += datetime.timedelta(days=1)
            temp_tipo_dia = get_tipo_dia(fecha_primer_dia)

        return fecha_primer_dia.strftime("%Y-%m-%d")



def calculoNoLetras(cotPlazo, auxPeriocidad):
    return cotPlazo * auxPeriocidad





def calculoTasaEfectiva(calcMontoLetra,auxPeriocidad,tablaTotalInteres,cotMontoPrestamo,auxPlazoPago,params):

    pagaDiciembre2 = "N"
    auxM = 0
    montoManejoB = 2120.04 #VERIFICAR

    #print("----TASA EFECTIVA MENSUAL----")

    if(pagaDiciembre2=="Y"):
        auxM = 11
    else:
        auxM=12 

    aux0 = auxPeriocidad * calcMontoLetra
    sobresaldo = "Y"
    
    if(sobresaldo == "Y"):
        wrkInteresTotal = round(tablaTotalInteres,2)
        wrkTasaEfectiva = wrkInteresTotal
    else:
        pass
    wrkInteresTotal = round(wrkInteresTotal * 100) / 100
    montoManejoB = round(montoManejoB * 100) / 100
    wrkTasaEfectiva = wrkTasaEfectiva + montoManejoB
    wrkTasaEfectiva = wrkTasaEfectiva * 2
    wrkTasaEfectiva = wrkTasaEfectiva * auxM
    wrkTasaEfectiva = round(wrkTasaEfectiva * 100) / 100

    auxV = 0
    calcNetoCancelac = params['calcNetoCancelacion']
    calcMontoRefi = 0
    calcDevInteres = 0
    calcDevSeguro = 0
    auxP = cotMontoPrestamo

    auxP = auxP + calcNetoCancelac
    auxP = auxP + calcMontoRefi
    auxP = auxP - calcDevInteres
    auxP = auxP - calcDevSeguro
    auxP = auxP - auxV

    auxN = auxPlazoPago + 1

    auxD = auxP * auxN

    wrkTasaEfectiva = wrkTasaEfectiva / auxD
    wrkTasaEfectiva = round(wrkTasaEfectiva, 6)

    if wrkTasaEfectiva <= 0.99:
        wrkTasaEfectiva = wrkTasaEfectiva * 100

    calcTasaEfectiva = wrkTasaEfectiva
    #print("Tasa Efectiva: ",calcTasaEfectiva)

    return calcTasaEfectiva


def recrearSobresaldo(cotMontoPrestamo,calcTasaInteres,auxPlazoPago,patrono,calcMonto2,auxPeriocidad,calcMontoTimbres,calcMontoNotaria,fechaInicioPago,tempPrimerDiaHabil,cotFechaInicioPago,calcFechaPromeCK,params):

        
    calcMontoNetoBruto = cotMontoPrestamo
    plazoPago = auxPlazoPago
    plazoInteres = plazoPago    
    tipopagoPeriocidad = auxPeriocidad
    pagadiciembre1 = "Y"

    params["calcMontoTimbres"] = calcMontoTimbres

    tablaTotalPagos, tablaTotalSeguro, tablaTotalFeci, tablaTotalInteres, tablaTotalMontoCapital, wrkMontoLetra, wrkLetraSeguro = tablaAmortizacion(params)

    
    params['tablaTotalPagos'] = tablaTotalPagos
    params['tablaTotalSeguro'] = tablaTotalSeguro
    params['tablaTotalFeci'] = tablaTotalFeci
    params['tablaTotalInteres'] = tablaTotalInteres
    params['tablaTotalMontoCapital'] = tablaTotalMontoCapital
    params['wrkMontoLetra'] = wrkMontoLetra
    params['wrkLetraSeguro'] = wrkLetraSeguro

    
    
    auxMensualidad = wrkMontoLetra
    auxMontoLetra2 = auxMensualidad / auxPeriocidad
    wrkMontoLetra = round(auxMontoLetra2,2)
    calcMontoLetra = wrkMontoLetra

    calcTasaEfectiva = calculoTasaEfectiva(wrkMontoLetra,auxPeriocidad,tablaTotalInteres,cotMontoPrestamo,auxPlazoPago,params)
    #print("Tasa Efectiva: ",calcTasaEfectiva)
    wrkLogic10 = "Y"
    if(wrkLogic10=="Y"):
        
        TasaEfectiva,r1 = calculoRentabilidad(fechaInicioPago,tempPrimerDiaHabil,params)

    #print("Tasa Efectiva: ",round(TasaEfectiva*100,2)," r1: ",round(r1*100,2))
    #print("total pagos: ",tablaTotalPagos," total seguro: ",tablaTotalSeguro," total feci: ",tablaTotalFeci," total interes: ",tablaTotalInteres," total monto capital: ",tablaTotalMontoCapital," monto letra: ",wrkMontoLetra)
    return r1

   
    
def rutinaCalculo(params):
   
    cotMontoPrestamo = params['cotMontoPrestamo']
    calcTasaInteres = params['calcTasaInteres']
    calcComiCierre = params['calcComiCierre']
    auxPlazoPago = params['auxPlazoPago']
    edad = params['edad']
    patrono = params['patrono']
    calcMontoNotaria = params['calcMontoNotaria']
    calcFechaPromeCK = params['calcFechaPromeCK']
  
    
    auxPeriocidad = 1
    #calcMontoTimbres=17.60
    
    
    #manejo_5porc=148.40
    fechaInicioPago = datetime.datetime(2025, 1, 5)
    tempPrimerDiaHabil = datetime.datetime(2024, 11, 1)
    cotFechaInicioPago = datetime.datetime(2024, 12, 30)
    
    pagadiciembre1 = "Y"
    forma_pago = 4
    codigoSeguro = 7
    
    auxPlazoInteres = auxPlazoPago
    #Neto Cancelacion
    if params['financiaSeguro'] == True:
        calcNetoCancelacion = params['montoMensualSeguro'] * params['mesesFinanciaSeguro']
        params['calcNetoCancelacion'] = calcNetoCancelacion
    else:
        calcNetoCancelacion = 0
        params['calcNetoCancelacion'] = calcNetoCancelacion


    #determinar monto amortizar
    aux_l, aux_z, aux_x, calcComiCierre,tasaBruta,tasaReal = determinar_monto_amortizar(cotMontoPrestamo, calcMontoNotaria, calcComiCierre, "PREST AUTO",codigoSeguro,edad,calcNetoCancelacion)
    #print("aux_l: ",aux_l," aux_z: ",aux_z," aux_x: ",aux_x," calcComiCierre: ",calcComiCierre)
    params['calcComiCierreFinal'] = calcComiCierre
    params['tasaBruta'] = tasaBruta
    calcMonto2 = aux_x
    params['auxMonto2'] = calcMonto2

    #CALCULO MENSUALIDAD SOBRESALDO
    wrkMontoLetra=calculoMensualidadSobresaldo(auxPlazoPago,calcMonto2,calcTasaInteres)
    params['wrkMontoLetra'] = wrkMontoLetra

    #CALCULO SOBRESALDO EN CALCULO
    params =calculoSobresaldoEnCalculo(auxPlazoPago,cotMontoPrestamo,calcTasaInteres,calcMonto2,calcComiCierre,calcMontoNotaria,params)
    
    #print(params)
    #PENDIENTE TOTAL SEGURO
    totalSeguro, montoSeguro, seguroAdicional = calculoSeguroTotal(calcMonto2,tasaBruta,tasaReal,auxPlazoInteres)
    #print("Total Seguro: ",totalSeguro," Monto Seguro: ",montoSeguro)
    params['totalSeguro'] = totalSeguro
    params['seguroAdicional'] = seguroAdicional

    #DIAS FECI
    diasFeci = calculoDiasFECI(auxPlazoPago)
    #print(diasFeci)
    
    #FECHA VENCIMIENTO
    fecha_vencimiento = calculate_fecha_vencimiento(auxPlazoPago, cotFechaInicioPago, pagadiciembre1, forma_pago)
    #print("fecha_vencimiento: ",fecha_vencimiento)
    
    #RECREAR SOBRESALDO
    calcMontoTimbres = params['calcMontoTimbres']
    r1= recrearSobresaldo(cotMontoPrestamo,calcTasaInteres,auxPlazoPago,patrono,calcMonto2,auxPeriocidad,calcMontoTimbres,calcMontoNotaria,fechaInicioPago,tempPrimerDiaHabil,cotFechaInicioPago,calcFechaPromeCK,params)
    return r1, params


def generarFideicomiso():

    params = {
        'cotMontoPrestamo': 15000,
        'calcTasaInteres': 10 / 100,
        'calcComiCierre': 13 / 100,
        'auxPlazoPago': 86,
        'edad': 46,
        'patrono': 512,
        'sucursal': 13,
        'auxPeriocidad': 1,
        'forma_pago': 4,
        'codigoSeguro': 7,
        'auxperiocidad': 1,
        'fechaCalculo': datetime.datetime.now(),
    }
    
    patrono = params['patrono']
    sucursal = params['sucursal']
    forma_pago = params['forma_pago']
    
    fechaCalculo = datetime.datetime.now() + datetime.timedelta(days=31)
    #print("Fecha Calculo: ",fechaCalculo)
    params['cotFechaInicioPago'] = fechaCalculo

    #PAGA DICIEMBRE
    pagaDiciembre = paga_diciembre(patrono, "PREST AUTO", forma_pago, "SI")
    
    #CALCULO PLAZO MAXIMO

    #IDENTIFGICAR NOTARIA
    notaria = identificar_notaria(sucursal, params['cotMontoPrestamo'], "PREST AUTO", 100, patrono, "")
    #print("Notaria: ",notaria)

    calcMontoNotaria = search_gasto(notaria)
    #print("Monto Notaria: ",calcMontoNotaria)

    #FECHA PROMESA 
    #fecha_promesa = calculate_fecha_promesa_ck(patrono, 10, 5, fechaCalculo, "2024-11-01", "2026-12-11")
    fecha_promesa = calculoFechaPromesa()
    #print("Fecha Promesa: ",fecha_promesa)
    
    #add calcMontoNotaria to params
    params['calcFechaPromeCK'] = fecha_promesa
    params['calcMontoNotaria'] = calcMontoNotaria
    
    #RUTINA CALCULO
    r1 =rutinaCalculo(params)


    return


def generarFideicomiso2(params):
    try:
        logger.info("Starting generarFideicomiso3 with params: %s", params)
        
        patrono = params['patrono']
        sucursal = params['sucursal']
        forma_pago = params['forma_pago']

        fechaCalculo = datetime.datetime.now() + datetime.timedelta(days=31)
        params['cotFechaInicioPago'] = fechaCalculo

        logger.info("Fecha Calculo set to: %s", fechaCalculo)

        # PAGA DICIEMBRE
        pagaDiciembre = paga_diciembre(patrono, "PREST AUTO", forma_pago, "SI")
        logger.info("Paga Diciembre: %s", pagaDiciembre)

        # IDENTIFICAR NOTARIA
        notaria = identificar_notaria(sucursal, params['cotMontoPrestamo'], "PREST AUTO", 100, patrono, "")
        calcMontoNotaria = search_gasto(notaria)
        logger.info("Calc Monto Notaria: %s", calcMontoNotaria)

        # FECHA PROMESA
        fecha_promesa = calculoFechaPromesa()
        logger.info("Fecha Promesa: %s", fecha_promesa)

        # Add calcMontoNotaria to params
        params['calcFechaPromeCK'] = fecha_promesa
        params['calcMontoNotaria'] = calcMontoNotaria

        # Goal seeking algorithm
        desired_r1 = params['r_deseada']
        tolerance = 0.00005  # Define a tolerance level for the desired r1 value
        max_iterations = 400  # Define a maximum number of iterations to prevent infinite loops
        iteration = 0
        while iteration < max_iterations:
            r1, resultados = rutinaCalculo(params)
            logger.info("Iteration %d: r1 = %s, desired_r1 = %s", iteration, r1, desired_r1)
            print("Diferencia: ", abs(r1 - desired_r1))
            print("Diferencia: ", r1 - desired_r1)
            if r1 >= desired_r1 and abs(r1 - desired_r1) <= tolerance:
                break
            elif r1 < desired_r1:
                params['calcTasaInteres'] += 0.001  # Increase the interest rate
            else:
                params['calcTasaInteres'] -= 0.001  # Decrease the interest rate
            iteration += 1

        if iteration == max_iterations:
            print("Goal seeking algorithm did not converge within the maximum number of iterations.","tolerance: ",tolerance*100)
            while r1 < desired_r1:
                params['calcTasaInteres'] += 0.001  # Ensure r1 is above desired_r1
                r1, resultados = rutinaCalculo(params)
            resultados['r1'] = r1 * 100
            resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
            resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 2)
        else:
            logger.info("Desired r1 value achieved: %s with calcTasaInteres: %s", r1, params['calcTasaInteres'])
            print("Desired r1 value achieved: %s with calcTasaInteres: %s", r1, params['calcTasaInteres'],"tolerance: ",tolerance*100)
            resultados['r1'] = r1 * 100
            resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
            resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 2)

        return resultados
    except Exception as e:
        logger.error("Error in generarFideicomiso2: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        raise



def generarFideicomiso3(params):
    try:
        logger.info("Starting generarFideicomiso2 with params: %s", params)
        
        patrono = params['patrono']
        sucursal = params['sucursal']
        forma_pago = params['forma_pago']

        fechaCalculo = datetime.datetime.now() + datetime.timedelta(days=31)
        params['cotFechaInicioPago'] = fechaCalculo

        logger.info("Fecha Calculo set to: %s", fechaCalculo)

        # PAGA DICIEMBRE
        pagaDiciembre = paga_diciembre(patrono, "PREST AUTO", forma_pago, "SI")
        logger.info("Paga Diciembre: %s", pagaDiciembre)

        # IDENTIFICAR NOTARIA
        notaria = identificar_notaria(sucursal, params['cotMontoPrestamo'], "PREST AUTO", 100, patrono, "")
        calcMontoNotaria = search_gasto(notaria)
        logger.info("Calc Monto Notaria: %s", calcMontoNotaria)

        # FECHA PROMESA
        fecha_promesa = calculoFechaPromesa()
        logger.info("Fecha Promesa: %s", fecha_promesa)

        # Add calcMontoNotaria to params
        params['calcFechaPromeCK'] = fecha_promesa
        params['calcMontoNotaria'] = calcMontoNotaria

        # Goal seeking algorithm using binary search
        desired_r1 = params['r_deseada']
        tolerance = 0.00005  # Define a tolerance level for the desired r1 value
        max_iterations = 400  # Define a maximum number of iterations to prevent infinite loops
        iteration = 0

        # Set initial bounds for binary search
        lower_bound = 0.0
        upper_bound = 1.0
        params['calcTasaInteres'] = (lower_bound + upper_bound) / 2

        while iteration < max_iterations:
            r1, resultados = rutinaCalculo(params)
            logger.info("Iteration %d: r1 = %s, desired_r1 = %s", iteration, r1, desired_r1)
            print("Diferencia: ", abs(r1 - desired_r1))
            print("Diferencia: ", r1 - desired_r1)
            if abs(r1 - desired_r1) <= tolerance:
                break
            elif r1 < desired_r1:
                lower_bound = params['calcTasaInteres']
            else:
                upper_bound = params['calcTasaInteres']
            params['calcTasaInteres'] = (lower_bound + upper_bound) / 2
            iteration += 1

        if iteration == max_iterations:
            print("Goal seeking algorithm did not converge within the maximum number of iterations.","tolerance: ",tolerance*100)
            while r1 < desired_r1:
                params['calcTasaInteres'] += 0.001  # Ensure r1 is above desired_r1
                r1, resultados = rutinaCalculo(params)
                resultados['r1'] = r1 * 100
                resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
                resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 2)
        else:
            logger.info("Desired r1 value achieved: %s with calcTasaInteres: %s", r1, params['calcTasaInteres'])
            print("Desired r1 value achieved: %s with calcTasaInteres: %s", r1, params['calcTasaInteres'],"tolerance: ",tolerance*100)
            resultados['r1'] = r1 * 100
            resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
            resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 2)

        return resultados
    except Exception as e:
        logger.error("Error in generarFideicomiso2: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        raise


