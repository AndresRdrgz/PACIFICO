from datetime import datetime
from datetime import timedelta

from .searchRestriccion import search_restriccion, obtenerPorcentaje, search_idChasis





def obtenerPrima(limiteInferior,descuento):
    primas = [
        (5000, 10000, 12.95),
        (10000, 20000, 17.15),
        (25000, 50000, 24.50),
        (50000, 100000, 32.90),
        (100000, 300000, 41.30),
        (5000, 5000, 100.06),
        (10000, 10000, 112.66),
        (15000, 15000, 129.46),
        (20000, 20000, 137.86),
        (25000, 25000, 146.26),
        (50000, 50000, 154.66),
        (100000, 100000, 163.06),
        (500, 2500, 5.83),
        (1000, 5000, 8.17),
        (2000, 10000, 14.97),
        (5000, 25000, 21.39),
        (10000, 50000, 32.08)
    ]

    descuento =(1-descuento/100)

    for limiteInf, limiteSup, prima in primas:
        if limiteInferior <= limiteInf:
            print(prima)
            prima = prima * descuento
            return prima

    return None  # Return None if no matching range is found

def calculoAntiguedad(yearAuto):

    current_year = datetime.now().year
    
    ceroKM = 0
    tarif = yearAuto+ceroKM
    

    if (current_year - yearAuto) < 0:
        antiguedad = 0
    elif (current_year - yearAuto) >= 10:
        antiguedad = ">=10"
    else:
        antiguedad = current_year - yearAuto
    
    return antiguedad

def calcPrimaAntComprensivo(antiguedad,valorAuto):

    primaAntComprensivo = 0
    descuentos = {
        0: 1.3,
        1: 1.5,
        2: 1.7,
        3: 1.9,
        4: 2.2,
        5: 2.4,
        6: 2.7,
        7: 2.7,
        8: 2.7,
        9: 2.7,
        '>=10': 3.0
    }

    if antiguedad in descuentos:
        primaAntComprensivo = valorAuto * (descuentos[antiguedad] / 100)
    else:
        primaAntComprensivo = valorAuto * (descuentos['>=10'] / 100)

    
    print('primaAntCOmprensivo',primaAntComprensivo)
    return primaAntComprensivo

def calcPrimaAntColision(antiguedad,valorAuto):

    primaAntComprensivo = 0
    descuentos = {
        0: 3.2,
        1: 3.7,
        2: 4.2,
        3: 4.7,
        4: 5.3,
        5: 5.9,
        6: 6.5,
        7: 6.5,
        8: 6.5,
        9: 6.5,
        '>=10': 7.0
    }

    if antiguedad in descuentos:
        primaAntColision = valorAuto * (descuentos[antiguedad] / 100)
    else:
        primaAntColision = valorAuto * (descuentos['>=10'] / 100)

    
    print('primaAntCOmprensivo',primaAntColision)
    return primaAntColision


def lesionesCorporales(params):
   

    #ANTIGUEDAD
    params['antiguedad'] = calculoAntiguedad(params['yearAuto'])
    print("Antiguedad: ", params['antiguedad'])

    #valor
    rangoSA,limiteInf,limiteSup = obtenerRangoSA(params['valor'])
    params['rangoSA'] = rangoSA
    params['limiteInf'] = limiteInf
    params['limiteSup'] = limiteSup
    params['rangoValorAuto'] = "[" + str(limiteInf) + "," + str(limiteSup) + "]"
    print(params['rangoValorAuto'])
    
    #rpima ant ocmprensivo
    params['primaAntComprensivo']=calcPrimaAntComprensivo(params['antiguedad'],params['valor'])
    #prima ant colision
    params['primaAntColision']=calcPrimaAntColision(params['antiguedad'],params['valor'])
    
    #years vehiculo
    yearsDelVehiculo = params['current_year'] - params['yearAuto']
    params['yearsDelVehiculo'] = yearsDelVehiculo
    #restriccion
    params['porRestriccion']= search_restriccion(params['marca'],params['modelo'])
    print(params['porRestriccion'])
    #CHASIS
    params['codMarca'] = search_idChasis(params['marca'],params['modelo'])
    #Count characters of codMarca
    params['numCaracteresCodMarca'] = len(str(params['codMarca']))
    print('numCaracteresCodMarca', params['numCaracteresCodMarca'])
    
    if params['numCaracteresCodMarca'] == 7:
        params['idChasis'] = str(params['codMarca'])[2:4]  # Ensure codMarca is a string before slicing
    else:
        params['idChasis'] = str(params['codMarca'])[3:5]
    
    print('idChasis',params['idChasis'])
    params['porcentajeChasis'] = obtenerPorcentaje(params['idChasis'])

    # Convert porcentajeChasis to float
    params['porcentajeChasis'] = float(params['porcentajeChasis'].strip('%')) / 100
    print(params['porcentajeChasis'])

    #DESCUENTO
    descuentos_antiguedad = {
        0: -24.0,
        1: -20.0,
        2: -16.0,
        3: -12.0,
        4: -8.0,
        5: -4.0,
        6: 0.0,
        7: 4.0,
        8: 8.0,
        9: 12.0,
        '>=10': 16.0
    }

    if params['antiguedad'] in descuentos_antiguedad:
        params['descuentoAntiguedad'] = descuentos_antiguedad[params['antiguedad']]
    else:
        params['descuentoAntiguedad'] = descuentos_antiguedad['>=10']

    print("Descuento Antiguedad: ", params['descuentoAntiguedad'])
    
    # Apply discount based on rangoValorAuto
    descuento_rango = {
        "[0,5000]": -10.0,
        "[5000,10000]": -12.0,
        "[10000,15000]": -15.0,
        "[15000,20000]": -18.0,
        "[20000,25000]": -20.0,
        "[25000,30000]": -23.0,
        "[30000,35000]": -24.5,
        "[35000,40000]": -26.0,
        "[40000,45000]": -27.0,
        "[45000,50000]": -28.5,
        "[50000,55000]": -29.0,
        ">55000": -30.0
    }

    params['descuentoRango'] = descuento_rango.get(params['rangoValorAuto'], 0)
    print("Descuento Rango: ", params['descuentoRango'])

    #Calculo descuento
    calculoDescuento = params['descuentoRango'] + params['descuentoAntiguedad']
    calculoDescuento = calculoDescuento * (-1)
    calculoDescuento = min(calculoDescuento, 70)
    print("Calculo Descuento: ", calculoDescuento)

    descuento = calculoDescuento - params['porRestriccion']*100- params['porcentajeChasis']*100 + params['descuentoLesionesCorporales']*100
    params['descuentoLesionesCorp'] = descuento
    print("Descuento Lesiones Corporales: ", descuento)
    
    return params

#calculoSeguroAuto()
def obtenerRangoSA(valorAuto):
    rangos = [
        (0, 5000, "-10.0%"),
        (5000, 10000, "-12.0%"),
        (10000, 15000, "-15.0%"),
        (15000, 20000, "-18.0%"),
        (20000, 25000, "-20.0%"),
        (25000, 30000, "-23.0%"),
        (30000, 35000, "-24.5%"),
        (35000, 40000, "-26.0%"),
        (40000, 45000, "-27.0%"),
        (45000, 50000, "-28.5%"),
        (50000, 55000, "-29.0%"),
        (55000, float('inf'), "-30.0%")
    ]

    for limiteInf, limiteSup, rangoSA in rangos:
        if limiteInf <= valorAuto < limiteSup:
            return rangoSA, limiteInf, limiteSup

    return None  # Return None if no matching range is found
