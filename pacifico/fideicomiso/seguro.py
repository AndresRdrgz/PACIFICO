from datetime import datetime, timedelta

def auxBusquedaSeguro(codigo, edad):
    # Define the table as a list of dictionaries
    table = [
        {"CODIGO": 7, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO H", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 59, "TASABRUTA": 0.75, "SOBRETASA": None, "TASAREAL": 0.75},
        {"CODIGO": 7, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO H", "SECUENCIA": 2, "EDAD MIN": 60, "EDAD MAX": 61, "TASABRUTA": 2, "SOBRETASA": None, "TASAREAL": 2},
        {"CODIGO": 7, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO H", "SECUENCIA": 3, "EDAD MIN": 62, "EDAD MAX": 99, "TASABRUTA": 0, "SOBRETASA": None, "TASAREAL": None},
        {"CODIGO": 8, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO M", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 57, "TASABRUTA": 0.75, "SOBRETASA": None, "TASAREAL": 0.75},
        {"CODIGO": 8, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO M", "SECUENCIA": 2, "EDAD MIN": 59, "EDAD MAX": 99, "TASABRUTA": 0, "SOBRETASA": None, "TASAREAL": None},
    ]

    # Find the matching row in the table
    for row in table:
        if row["CODIGO"] == codigo and row["EDAD MIN"] <= edad <= row["EDAD MAX"]:
            return row["TASABRUTA"], row["SOBRETASA"], row["TASAREAL"]

    # Return None if no match is found
    return None, None, None

def seguroAdicional():

        def getLastDayOfMonth(date):
            next_month = date.replace(day=28) + timedelta(days=4)
            return next_month - timedelta(days=next_month.day)

        wrkFechaUltDia1 = datetime(2024, 12, 11)
        wrkFechaUltDia2 = datetime(2024, 12, 30)
        wrkFechaUltDia2 = getLastDayOfMonth(wrkFechaUltDia2)

        auxW = 1
        auxZ = 0
        auxBol = True

        while auxBol:
            wrkFechaUltDia1_aux = wrkFechaUltDia1
            wrkFechaUltDia1 = wrkFechaUltDia1.replace(day=28) + timedelta(days=4)
            wrkFechaUltDia1 = wrkFechaUltDia1.replace(day=1) + timedelta(days=auxW * 30)
            
            if wrkFechaUltDia1 <= wrkFechaUltDia2:
                auxW += 1
                auxZ += 1
                wrkFechaUltDia1 = wrkFechaUltDia1_aux
                auxBol = True
            else:
                auxBol = False

        if auxZ >= 1:
            auxZ -= 1

        return auxZ
    


def calculoSeguroTotal(auxMonto2,auxTasaBruta,auxTasaReal,auxPlazoInteres):
    
    
    
    auxA = auxMonto2
    auxB = auxTasaBruta
    auxG = 0
    auxC = 0
    wrkC = 0
    auxZ = seguroAdicional()
    
    auxX = 0
    wrkWorkD = auxTasaReal
    monto2 = auxMonto2
    wrkPorcSeguroTotal = auxTasaBruta
    sobresaldo = "Y"
    agregado = ""
    descomponer2 = 1.05
    tipo_prestamo = "PREST AUTO"

    if auxC != 0:
        auxA = ((auxA * auxB * auxC) / 1000)
        auxX = ((auxA * auxB * auxG) / 1000)
        montoSeguro = auxA
        wrkWorkD = auxX
        monto2 = monto2 - montoSeguro
    else:
        montoSeguro = 0
    
    auxA = monto2
    auxB = wrkPorcSeguroTotal
    auxC = auxPlazoInteres
    auxC = auxC + auxZ

    auxA = ((auxA * auxB * auxC) / 1000)
    auxX = ((auxA * auxB * auxG) / 1000)
    totalSeguro = auxA
    wrkSaldo13 = auxX

    # CALCULO DEL SEGURO 5%
    if sobresaldo == "Y":
        totalSeguro = round(totalSeguro * 100) / 100
        totalSeguro = totalSeguro * descomponer2
        totalSeguro = round(totalSeguro * 100) / 100

    if agregado == "Y":
        montoSeguro = montoSeguro * descomponer2
    
    return totalSeguro, montoSeguro, auxZ

    return