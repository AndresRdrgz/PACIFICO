from datetime import datetime, timedelta

def auxBusquedaSeguro(codigo, edad):
    # Define the table as a list of dictionaries
    table = [
        {"CODIGO": 4, "DESCRIPCION": "INTERNACIONAL DE SEGUROS", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 50, "TASABRUTA": 2, "SOBRETASA": 1.65, "TASAREAL": 0.35},
        {"CODIGO": 4, "DESCRIPCION": "INTERNACIONAL DE SEGUROS", "SECUENCIA": 2, "EDAD MIN": 51, "EDAD MAX": 60, "TASABRUTA": 2.5, "SOBRETASA": 1.5, "TASAREAL": 1},
        {"CODIGO": 4, "DESCRIPCION": "INTERNACIONAL DE SEGUROS", "SECUENCIA": 3, "EDAD MIN": 61, "EDAD MAX": 70, "TASABRUTA": 2, "SOBRETASA": 1.25, "TASAREAL": 0.75},
        {"CODIGO": 4, "DESCRIPCION": "INTERNACIONAL DE SEGUROS", "SECUENCIA": 4, "EDAD MIN": 71, "EDAD MAX": 99, "TASABRUTA": 3.5, "SOBRETASA": 1.5, "TASAREAL": 2},
        {"CODIGO": 7, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO H", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 59, "TASABRUTA": 0.75, "SOBRETASA": None, "TASAREAL": 0.75},
        {"CODIGO": 7, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO H", "SECUENCIA": 2, "EDAD MIN": 60, "EDAD MAX": 61, "TASABRUTA": 2, "SOBRETASA": None, "TASAREAL": 2},
        {"CODIGO": 7, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO H", "SECUENCIA": 3, "EDAD MIN": 62, "EDAD MAX": 99, "TASABRUTA": 0, "SOBRETASA": None, "TASAREAL": None},
        {"CODIGO": 8, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO M", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 57, "TASABRUTA": 0.75, "SOBRETASA": None, "TASAREAL": 0.75},
        {"CODIGO": 8, "DESCRIPCION": "INTERNACIONAL DE SEGUROS - FIDEICOMISO M", "SECUENCIA": 2, "EDAD MIN": 58, "EDAD MAX": 99, "TASABRUTA": 0, "SOBRETASA": None, "TASAREAL": None},
        {"CODIGO": 10, "DESCRIPCION": "SOBRETASA 2%", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 99, "TASABRUTA": 2, "SOBRETASA": 2, "TASAREAL": 2},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 49, "TASABRUTA": 2, "SOBRETASA": 0.5, "TASAREAL": 1.5},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 2, "EDAD MIN": 50, "EDAD MAX": 66, "TASABRUTA": 2.5, "SOBRETASA": 1, "TASAREAL": 1.5},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 3, "EDAD MIN": 67, "EDAD MAX": 69, "TASABRUTA": 3.5, "SOBRETASA": 1, "TASAREAL": 2.5},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 4, "EDAD MIN": 70, "EDAD MAX": 70, "TASABRUTA": 4.5, "SOBRETASA": 1.5, "TASAREAL": 3},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 5, "EDAD MIN": 71, "EDAD MAX": 72, "TASABRUTA": 6.5, "SOBRETASA": 2, "TASAREAL": 4.5},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 6, "EDAD MIN": 73, "EDAD MAX": 75, "TASABRUTA": 7.5, "SOBRETASA": 3, "TASAREAL": 4.5},
        {"CODIGO": 19, "DESCRIPCION": "ASEGURADORA MUNDIAL (ENE-2005)", "SECUENCIA": 7, "EDAD MIN": 76, "EDAD MAX": 79, "TASABRUTA": 8.5, "SOBRETASA": 3, "TASAREAL": 5.5},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 49, "TASABRUTA": 2, "SOBRETASA": 0.5, "TASAREAL": 1.5},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 2, "EDAD MIN": 50, "EDAD MAX": 66, "TASABRUTA": 2.5, "SOBRETASA": 1, "TASAREAL": 1.5},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 3, "EDAD MIN": 67, "EDAD MAX": 69, "TASABRUTA": 3.5, "SOBRETASA": 1, "TASAREAL": 2.5},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 4, "EDAD MIN": 70, "EDAD MAX": 70, "TASABRUTA": 4.5, "SOBRETASA": 1.5, "TASAREAL": 3},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 5, "EDAD MIN": 71, "EDAD MAX": 72, "TASABRUTA": 6.5, "SOBRETASA": 2, "TASAREAL": 4.5},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 6, "EDAD MIN": 73, "EDAD MAX": 75, "TASABRUTA": 7.5, "SOBRETASA": 3, "TASAREAL": 4.5},
        {"CODIGO": 20, "DESCRIPCION": "ASEGURADORA MUNDIAL (JULIO-2005)", "SECUENCIA": 7, "EDAD MIN": 76, "EDAD MAX": 79, "TASABRUTA": 8.5, "SOBRETASA": 3, "TASAREAL": 5.5},
        {"CODIGO": 99, "DESCRIPCION": "SIN SEGURO", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 99, "TASABRUTA": 0, "SOBRETASA": 0, "TASAREAL": 0},
        {"CODIGO": 99, "DESCRIPCION": "ADELA DOBLES (INTERIOR)", "SECUENCIA": 1, "EDAD MIN": 18, "EDAD MAX": 79, "TASABRUTA": 10, "SOBRETASA":3, "TASAREAL":7},
    ]

    ##print(("codigo:",codigo,"edad:",edad)
    # Find the matching row in the table
    for row in table:
        if row["CODIGO"] == codigo and row["EDAD MIN"] <= edad <= row["EDAD MAX"]:
            #print(("Seguro encontrado:", row["DESCRIPCION"], row["TASABRUTA"], row["SOBRETASA"], row["TASAREAL"])
            
            return row["TASABRUTA"], row["SOBRETASA"], row["TASAREAL"]

    # Return None if no match is found
    #print(("No se encontró el seguro",codigo,edad)
    
    return None, None, None

def seguroAdicional(calcFechaPromeCK,cotFechaInicioPago):

        def getLastDayOfMonth(date):
            next_month = date.replace(day=28) + timedelta(days=4)
            return next_month - timedelta(days=next_month.day)

        wrkFechaUltDia1 = calcFechaPromeCK.date()
        wrkFechaUltDia2 = cotFechaInicioPago.date()
        #print(("wrkFechaUltDia1:",wrkFechaUltDia1,"wrkFechaUltDia2:",wrkFechaUltDia2)
       
        wrkFechaUltDia2 = getLastDayOfMonth(wrkFechaUltDia2)
        #print(("wrkFechaUltDia2",wrkFechaUltDia2)
        
        auxW = 1
        auxZ = 0
        auxBol = True

        while auxBol:
            wrkFechaUltDia1_aux = wrkFechaUltDia1
            wrkFechaUltDia1 = wrkFechaUltDia1.replace(day=28) + timedelta(days=4)
            wrkFechaUltDia1 = wrkFechaUltDia1.replace(day=1) + timedelta(days=auxW * 30)
            #print(("wrkFechaUltDia1:",wrkFechaUltDia1,"<= wrkFechaUltDia2:",wrkFechaUltDia2)
            
            
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
    


def calculoSeguroTotal(auxMonto2,auxTasaBruta,auxTasaReal,auxPlazoInteres,calcFechaPromeCK,cotFechaInicioPago):
    
    
    
    auxA = auxMonto2
    auxB = auxTasaBruta
    auxG = 0
    auxC = 0
    wrkC = 0
    auxZ = seguroAdicional(calcFechaPromeCK,cotFechaInicioPago)
    
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
    #print(("auxa:",auxA,"auxB:",auxB,"auxC:",auxC)
    
    auxA = ((auxA * auxB * auxC) / 1000)
    auxX = ((auxA * auxB * auxG) / 1000)
    totalSeguro = auxA 
    totalSeguro = round(totalSeguro,2)
    wrkSaldo13 = auxX

    # CALCULO DEL SEGURO 5%
    if sobresaldo == "Y":
        totalSeguro = round(totalSeguro * 100) / 100
        totalSeguro = totalSeguro * descomponer2
        totalSeguro = round(totalSeguro * 100) / 100

    if agregado == "Y":
        montoSeguro = montoSeguro * descomponer2
    
    #print(("totalSeguro:",totalSeguro)
   
    
    return totalSeguro, montoSeguro, auxZ