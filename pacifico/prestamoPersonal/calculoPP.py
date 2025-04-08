


import logging
import traceback
import datetime
from ..fideicomiso.fideicomiso import paga_diciembre, identificar_notaria, rutinaCalculo
from ..fideicomiso.notaria import search_gasto
from .. fideicomiso.fechaPromesaCK import checkDiaHabil
from datetime import datetime, timedelta


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



def calculoFechaPromesa_PP():
    no_patrono = 512
    diasprom1 = 10
    diasprom2 = 5
    fechaCalculo = datetime.now()
    ii = 0
    auxLibres = 0

    if 638 <= no_patrono <= 654 and no_patrono != 646:
        ii = diasprom2
    else:
        ii = diasprom1

    if no_patrono == 620:
        ii += 4

    for i in range(1, ii + 1):
            
        tipoDia = checkDiaHabil(fechaCalculo)
        #print(f"TIPO DIA for {fechaCalculo.strftime('%Y-%m-%d')}: {tipoDia}")
        if tipoDia == "HABIL":
            pass
        else:
            #add one day to fechaCalculo
            fechaCalculo += timedelta(days=1)
            auxLibres += 1
        fechaCalculo += timedelta(days=1)
    
    tipoDia = checkDiaHabil(fechaCalculo)
    if tipoDia != "HABIL":
        fechaCalculo += timedelta(days=1)
        auxLibres += 1
    
    
    #print(f"Fecha promesa: {fechaCalculo.strftime('%Y-%m-%d')}")
    return fechaCalculo
        

    

def generarPP(params):
    try:
        print("Starting generarPP with params:", params)
        
        patrono = params['patrono']
        sucursal = params['sucursal']
        forma_pago = params['forma_pago']

        if params['tipoPrestamo'] == "PREST AUTO":
            fechaCalculo = datetime.now() + timedelta(days=31)
            params['cotFechaInicioPago'] = fechaCalculo
        else:
            fechaCalculo = datetime.combine(params['fecha_inicioPago'], datetime.min.time())
            #print year, month and day
            #print("---------")
            #print(fechaCalculo.year, fechaCalculo.month, fechaCalculo.day)
            params['cotFechaInicioPago'] = fechaCalculo
            

        # PAGA DICIEMBRE
        pagaDiciembre = params['pagaDiciembre']
        pagaDiciembre = paga_diciembre(patrono, "PERSONAL", forma_pago, pagaDiciembre)
        print("Paga Diciembre: ", pagaDiciembre)

        # IDENTIFICAR NOTARIA
        notaria = identificar_notaria(sucursal, params['cotMontoPrestamo'], "PERSONAL", 100, patrono, "")
        print("Notaria: ", notaria)
        calcMontoNotaria = search_gasto(notaria)
        print("Calc Monto Notaria: ", calcMontoNotaria)

        # FECHA PROMESA
        fecha_promesa = calculoFechaPromesa_PP()
        print("Fecha Promesa: ", fecha_promesa)

        # Add calcMontoNotaria to params
        params['calcFechaPromeCK'] = fecha_promesa
        params['calcMontoNotaria'] = calcMontoNotaria

        #GOSUB :FECHA SERVICIO DE DESCUENTO

        # Goal seeking algorithm using binary search
        desired_r1 = params['r_deseada']
        print("Desired r1: ", desired_r1)
        tolerance = 0.000001  # Define a tolerance level for the desired r1 value
        max_iterations = 50  # Define a maximum number of iterations to prevent infinite loops
        iteration = 0

        # Set initial bounds for binary search
        lower_bound = 0.0
        #upper_bound = 0.65
        upper_bound = 1.0
        if max_iterations > 1:
            params['calcTasaInteres'] = (lower_bound + upper_bound) / 2
            params['calcTasaInteres'] = round(params['calcTasaInteres'], 4)
            params['calcTasaInteres'] = 0.1 # Set initial value for calcTasaInteres PRUEBAS PERASTAMO PERSONAL
        
            print("EMPEZAR CALCULO Tasa: ",params['calcTasaInteres'])
            
            #print(params)
            
            #count all fields in params
            i =0
            for key in params:
                i=i+1
            #print("Total de campos: ",i)
            while iteration < max_iterations:
                r1, resultados, iteration_data = rutinaCalculo(params)
                logger.info("Iteration %d: r1 = %s, desired_r1 = %s", iteration, r1, desired_r1)
                #print("Diferencia: ", abs(r1 - desired_r1))
                #print("Diferencia: ", r1 - desired_r1)
                #print("Iteracion: ",iteration, "tasa: ",params['calcTasaInteres']*100,"r1: ",r1*100)
                if abs(r1 - desired_r1) <= tolerance:
                    break
                elif r1 < desired_r1:
                    lower_bound = params['calcTasaInteres']
                else:
                    upper_bound = params['calcTasaInteres']
                params['calcTasaInteres'] = (lower_bound + upper_bound) / 2
                params['calcTasaInteres'] = round(params['calcTasaInteres'], 4)
                iteration += 1
                #print("Iteracion: ",iteration, "tasa: ",params['calcTasaInteres']*100,"r1: ",r1*100)

            if iteration == max_iterations:
                print("Goal seeking algorithm did not converge within the maximum number of iterations.","tolerance: ",tolerance*100)
                print("Tasa de interes: ",params['calcTasaInteres'],"ITERACIONES: ",iteration)
                resultados['r1'] = r1 * 100
                resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
                resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 4)

                while r1 < desired_r1:
                    params['calcTasaInteres'] += 0.001  # Ensure r1 is above desired_r1
                    r1, resultados,iteration_data = rutinaCalculo(params)
                    resultados['r1'] = r1 * 100
                    resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
                    resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 4)
            else:
                logger.info("Desired r1 value achieved: %s with calcTasaInteres: %s", r1, params['calcTasaInteres'])
                print("Desired r1 value achieved: %s with calcTasaInteres: %s", r1, "Tasa interes: ",params['calcTasaInteres']*100,"tolerance: ",tolerance*100,"iteraciones: ",iteration)
                resultados['r1'] = r1 * 100
                resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
                resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 4)
        else:
            r1, resultados,iteration_data = rutinaCalculo(params)
            resultados['r1'] = r1 * 100
            resultados['tasaEstimada'] = params['calcTasaInteres'] * 100
            resultados['tasaEstimada'] = round(resultados['tasaEstimada'], 4)

            
        return resultados,iteration_data
    except Exception as e:
        logger.error("Error in generarFideicomiso3: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        raise


