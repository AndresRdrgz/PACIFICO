from datetime import datetime
from datetime import timedelta
from .SURA.lesionesCorporales import lesionesCorporales, obtenerPrima


def primaGastosMedicos(limiteInferior,descuento):
    primas = [
        (500, 5.83),
        (1000, 8.17),
        (2000, 14.97),
        (5000, 21.39),
        (10000, 32.08)
    ]

    descuento =(1-descuento/100)

    for limiteInf, prima in primas:
        if limiteInferior <= limiteInf:
            print(prima)
            prima = prima * descuento
            return prima

    return None  # Return None if no matching range is found


def primaDanosPropiedad(limiteInferior,descuento):
    primas = [
        (5000, 100.06),
        (10000, 112.66),
        (15000, 129.46),
        (20000, 137.86),
        (25000, 146.26),
        (50000, 154.66),
        (100000, 163.06)
    ]

    descuento =(1-descuento/100)

    for limiteInf, prima in primas:
        if limiteInferior <= limiteInf:
            print(prima)
            prima = prima * descuento
            return prima

    return None  # Return None if no matching range is found



def cotizacionSeguroAuto(marca,modelo,yearAuto,valor,yearsFinanciamiento):

 
    params = {
        "marca": marca,
        "modelo": modelo,
        "yearAuto": yearAuto,
        "valor": valor,
        "yearsFinanciamiento": yearsFinanciamiento,
        "current_year": datetime.now().year,
        "descuentoLesionesCorporales": 0.2,
        "limitesLesionesCorporales": 10000,
        "limitesDanosPropiedad": 20000,
        "limitesGastosMedicos": 2000,

    }

    #LESIONES COPORALES
    params = lesionesCorporales(params)
    primaLesiones = obtenerPrima(params['limitesLesionesCorporales'],params['descuentoLesionesCorp'])
    print(params['descuentoLesionesCorp'])
    print(primaLesiones)
    #DANOS A LA PROPIEDAD
    primaDanos = primaDanosPropiedad(params['limitesDanosPropiedad'],params['descuentoLesionesCorp'])
    print(primaDanos)
    #GASTOS MEDICOS
    primaGastoMedico = primaGastosMedicos(params['limitesGastosMedicos'],params['descuentoLesionesCorp'])
    print(primaGastoMedico)
    #COMPRENSIVO
    com = 0.75/100
    if params['yearsDelVehiculo'] > 10:
        primaComprensivo = 0
    else:
        
        primaComprensivo = (valor*com) * (1-params['descuentoLesionesCorp']/100)

    print(primaComprensivo)
    
    #COLISION
    col = 3.6/100
    if params['yearsDelVehiculo'] > 10:
        primaColision = 0
    else:
        
        primaColision = (valor*col) * (1-params['descuentoLesionesCorp']/100)

    print(primaColision)
    
    #INCENDIO
    primaIncendio = 0
    #HURTO
    primaHurto = 0
    #COBERTURA SOAT
    primaSOAT = 30.25
    #ENDOSO FULL EXTRAS
    primaEndoso = 23.58

    #subtotal
    subtotal = primaLesiones + primaDanos + primaGastoMedico + primaComprensivo + primaColision + primaIncendio + primaHurto + primaSOAT + primaEndoso
    
    recargoHistorial = 0
    subtotal = subtotal + recargoHistorial
    impuesto = subtotal * 0.06
    total = subtotal + impuesto
    totalFinanciamiento = total * yearsFinanciamiento
    pago = total / 12

    total = round(total, 2)
    totalFinanciamiento = round(totalFinanciamiento, 2)
    pago = round(pago, 2)
    
    resultado = {
        "total": total,
        "totalFinanciamiento": totalFinanciamiento,
        "pago": pago,
    }

    return resultado

