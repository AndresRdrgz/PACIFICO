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

    print("Params initialized:", params)

    # LESIONES CORPORALES
    params = lesionesCorporales(params)
    print("Params after lesionesCorporales:", params)
    primaLesiones = obtenerPrima(params['limitesLesionesCorporales'], params['descuentoLesionesCorporales'])
    print("Prima Lesiones:", primaLesiones)

    # DANOS A LA PROPIEDAD
    primaDanos = primaDanosPropiedad(params['limitesDanosPropiedad'], params['descuentoLesionesCorporales'])
    print("Prima Danos:", primaDanos)

    # GASTOS MEDICOS
    primaGastoMedico = primaGastosMedicos(params['limitesGastosMedicos'], params['descuentoLesionesCorporales'])
    print("Prima Gasto Medico:", primaGastoMedico)

    # COMPRENSIVO
    com = 0.75 / 100
    if params['yearsDelVehiculo'] > 10:
        primaComprensivo = 0
    else:
        primaComprensivo = (valor * com) * (1 - params['descuentoLesionesCorporales'] / 100)
    print("Prima Comprensivo:", primaComprensivo)

    # COLISION
    col = 3.6 / 100
    if params['yearsDelVehiculo'] > 10:
        primaColision = 0
    else:
        primaColision = (valor * col) * (1 - params['descuentoLesionesCorporales'] / 100)
    print("Prima Colision:", primaColision)

    # INCENDIO
    primaIncendio = 0
    print("Prima Incendio:", primaIncendio)

    # HURTO
    primaHurto = 0
    print("Prima Hurto:", primaHurto)

    # COBERTURA SOAT
    primaSOAT = 30.25
    print("Prima SOAT:", primaSOAT)

    # ENDOSO FULL EXTRAS
    primaEndoso = 23.58
    print("Prima Endoso:", primaEndoso)

    # Subtotal
    subtotal = primaLesiones + primaDanos + primaGastoMedico + primaComprensivo + primaColision + primaIncendio + primaHurto + primaSOAT + primaEndoso
    print("Subtotal:", subtotal)

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

    print("Resultado:", resultado)

    return resultado
