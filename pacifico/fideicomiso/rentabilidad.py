import datetime
from decimal import Decimal, ROUND_HALF_UP


def rentabilidadEfectiva(calcMonto2,sobresaldo,wrkMontoFECI,wrkNum7_2,plazoPago,calcMontoNetoBruto,calcMontoTimbres,calcMontoNotaria,tipopagoPeriocidad,patrono,tipo_prestamo,calcTasaInteres,fechaInicioPago,plazoInteres,fechaCalculo,calcMontoLetra,calcInicioPago,tempPrimerDiaHabil,params):

    montoServDes = 0
    calcNetoCancelac = params['calcNetoCancelacion']
    calcMontoRefi = 0
    calcDevInteres = 0
    calcDevSeguro = 0
    

    pagadiciembre1 = "Y"

    print("----RENTABILIDAD EFECTIVA ----")
    print('calcMontoLetra:',calcMontoLetra)

    wrkMontoFECI = round(wrkMontoFECI, 2)
    wrkNum7_2 = round(wrkNum7_2, 2)
    
    if calcMonto2 >= 1000000:
        return

    if sobresaldo == "Y":
        pass

    auxQ = wrkMontoFECI / plazoPago
    wrkNetoTotal = calcMontoNetoBruto

    wrkNetoTotal += calcMontoTimbres
    wrkNetoTotal += montoServDes
    wrkNetoTotal += calcMontoNotaria
    wrkNetoTotal += calcNetoCancelac
    wrkNetoTotal += calcMontoRefi
    wrkNetoTotal += params['manejo_5porc']
    wrkNetoTotal -= calcDevInteres
    wrkNetoTotal -= calcDevSeguro
    
    wrkDes5Porciento = 0
    wrkFechaAnterior5 = datetime.datetime(2010, 6, 1)
    parimptoFechaSeguro1 = datetime.datetime(2010, 10, 9)
    wrkMonto21 = wrkDes5Porciento

    if tempPrimerDiaHabil >= wrkFechaAnterior5 and tempPrimerDiaHabil <= parimptoFechaSeguro1:
        wrkMonto21 *= 0.05
    else:
        wrkMonto21 *= 0.07

    
    
    wrkNetoTotal -= wrkMonto21

    wrkNetoTotal2 = wrkNetoTotal
    auxP = tipopagoPeriocidad

    auxW = 0
    wrkContador = 0

    auxL = 0.000102

    auxJ = 0
    print("auxp:",auxP)
    if patrono == 620 and tipo_prestamo != "LEASING":
        auxJ = calcMontoLetra
        auxJ = (auxJ * auxP) * 1.5 / 100

    auxX = calcTasaInteres
    auxX += 1
    auxX = pow(auxX, (1 / 12))
    wrkNumeric5_7 = auxX
    auxX = wrkNumeric5_7
    auxX = round(auxX - 1, 7)
    auxV = wrkNum7_2 / plazoPago
    auxX = round(auxX, 7)

    auxRepetir = True
    while auxRepetir:
        auxK = 0
        auxW += 1
        wrkMes = fechaInicioPago.month + 1
        wrkNum3 = wrkMes
        auxG = wrkNum3
        auxF = plazoPago
        auxO = 0

        auxB = plazoInteres
        wrkMonto = 0
        
        wrkFecha2 = datetime.datetime.strptime(fechaCalculo, '%Y-%m-%d') + datetime.timedelta(days=10)
        wrkFechaMesYear1 = wrkFecha2
        wrkFechaMesYear2 = calcInicioPago

        auxT = (wrkFechaMesYear1.year - wrkFechaMesYear2.year) * 12 + wrkFechaMesYear1.month - wrkFechaMesYear2.month

        agregado = "N"
        if agregado == "Y":
            pass

        if auxT <= 0:
            auxT = 1

        if sobresaldo == "Y":
            auxB = auxB + auxT - 1

        wrkNum9_2 = auxQ
        auxQ = wrkNum9_2
        wrkNum9_2 = auxV
        auxV = wrkNum9_2
        auxV = round(auxV, 2)
        auxQ = round(auxQ, 2)
        auxQI = 0
        auxE = calcMontoLetra
        auxE *= auxP
        auxE -= auxQ
        auxE -= auxV
        auxE -= auxJ
        auxS = auxE
        auxS = round(auxS, 2)
        auxA = auxT
        for auxA in range(auxT, auxB+1):
            if plazoPago == 1:
                if auxA == auxB:
                    pass
                else:
                    pass

            auxQI += 1
            auxE = auxS
            auxD = 1 + float(auxX)
            auxZ = auxD
            auxH = auxX
            ##print("auxH =", auxH,'auxqi:',auxQI,'auxs:',auxS)
           
    
            wrkAlpha4 = auxB
            if pagadiciembre1 == "Y" or wrkNum3 != 12:
                auxR = auxA
                auxD = pow(auxD, auxR)
                auxE = auxE / auxD
            else:
                auxE = 0
            
            
            rentableSecuencia = auxA
            rentableMes = wrkNum3
            rentableValor = auxE
            rentableValor = round(rentableValor, 2)
            
            
            

            if wrkNum3 != 12:
                wrkNum3 += 1
            else:
                wrkNum3 = 1

            wrkMonto += auxE
            wrkMonto = round(wrkMonto, 2)
            ##print('rentable valor',rentableValor,"wrkMonto =", wrkMonto)
            
            

        #wrkCredito5 = wrkDebito
       
        wrkDebito = wrkMonto
        wrkDebito -= wrkNetoTotal
        wrkDebito = round(wrkDebito, 2)
        
        

        wrkCredito = auxW

        if auxW == 99999:
            #print("auxW == 99999")
            return

        if calcMonto2 <= 100000:
            wrkIG = -0.10
        else:
            wrkIG = -0.30

        if calcMonto2 > 100000:
            wrkIG = -1

        if wrkDebito < 0.01:
            if wrkDebito < wrkIG:
                auxM = 0.000001
                auxL = 0.00000001
                auxX -= auxM
                auxRepetir = True
            else:
                auxRepetir = False
        else:
            auxX = float(auxX) + float(auxL)
            auxRepetir = True

    auxX = round(auxX, 7)

    wrkCredito2 = wrkDebito
    wrk1110 = auxH
    wrkRentaMensual = auxH
    auxY = auxH
    auxY *= 100
    calcRentabilidad = auxY
    auxU = auxY * 12
    calcRentaAnual = auxU

    calcRentaAnual = round(calcRentaAnual, 2)
    calcRentaAnual /= 100
    #print("calcRentaAnual = ", calcRentaAnual * 100)

    TasaEfectiva = calcRentaAnual

    return TasaEfectiva

def calculoRentabilidad(fechaInicioPago,tempPrimerDiaHabil,params):
    
    
    comisionVendedor = params['comisionVendedor']
    parmgralComisionPers = 50
    comisionTotal10 = parmgralComisionPers
    tipo_prestamo = "PREST AUTO"
    calcNetoCanc = params['calcNetoCancelacion']
    sobresaldo = "Y"
    pagadiciembre1 = "Y"
    calcMontoServDes2 = 0
    calcMontoServDes = 0
    calcMontoREFI = 0
    wrkDebito = 0
    auxFechaCalculo = datetime.datetime.now().strftime("%Y-%m-%d")
    fechaCalculo = auxFechaCalculo
    calcMontoNetoBruto = params['cotMontoPrestamo']
    manejo_5porc = params['manejo_5porc']
    patrono = params['patrono']
    calcMontoTimbres = params['calcMontoTimbres']
    calcMontoNotaria = params['calcMontoNotaria']
    plazoPago = params['auxPlazoPago']
    calcMontoLetra = params['wrkMontoLetra']
    calcTasaInteres = params['calcTasaInteres']
    tipopagoPeriocidad = params['auxPeriocidad']
    calcMonto2 = params['auxMonto2']
    tablaTotalFeci = params['tablaTotalFeci']
    tablaTotalSeguro = params['tablaTotalSeguro']
    calcFechaPromeCK = params['calcFechaPromeCK']
    cotFechaInicioPago = params['cotFechaInicioPago']
    plazoInteres = plazoPago
    
    ##print(params)
    

    comisionTotal10 = parmgralComisionPers
    
    if patrono in [642, 643, 649, 650]:
        comisionTotal10 = 10



    promoActiva = "Y"
    if promoActiva == "Y":
        promo_ini = datetime.datetime(2024, 1, 5)
        promo_fin = datetime.datetime(2024, 10, 31)
        fecha_calculo = datetime.datetime.strptime(auxFechaCalculo, "%Y-%m-%d")

        if promo_ini <= fecha_calculo <= promo_fin:
            # CALCULA PROMOCION
            #wrk_monto_pedido = calcular_promocion()
            #print("Calcular promocion")
            pass
        else:
            pass
    
    #SI ES CARTERA ACP
    if 630 <= patrono <= 660:
        wrkLogic4 = "Y"

    
    wrkMontoCancelAnt = 0
    wrkMontoPedido = 0
    claseVend = "SIN VENDEDOR"  # Example value, replace with actual value retrieval logic

    if claseVend == "CHISPA" and tipo_prestamo != "LEASING":
        # Add your logic here
        pass

    #Se le adiciona el 7% agencias promotoras
    comisionMonto = calcMontoNetoBruto
    comisionMonto = comisionMonto - calcNetoCanc
    comisionMonto = comisionMonto - wrkMontoCancelAnt
    comisionGastoComisio = 0
    comisionComision = [0] * 11  # Assuming a list with 11 elements
    comisionTotal = [0] * 11  # Assuming a list with 11 elements
    
    for auxH in range(1, 11):
        if auxH <= 6:
            if comisionComision[auxH] == "Y":
                # TT
                pass
            else:
                # FF
                comisionTotal[auxH] = 0
            comisionGastoComisio += comisionTotal[auxH]
    
    
    if sobresaldo == "Y":
        wrkMontoFECI=0
        wrkMontoFECI = tablaTotalFeci
        wrkNum7_2 = tablaTotalSeguro
        auxQ = wrkMontoFECI
    else:
        pass
    #print("wrkMontoFECI:",wrkMontoFECI,"wrkNum7_2:",wrkNum7_2)
    auxQ = auxQ / plazoPago
    auxQ = round(auxQ, 3)
    #print("auxQ =", auxQ)

    wrkNetoTotal = calcMontoNetoBruto
    
    wrkNetoTotal += calcMontoTimbres
    wrkNetoTotal += calcMontoServDes
    wrkNetoTotal += calcMontoServDes2
    wrkNetoTotal += calcMontoNotaria
    wrkNetoTotal += calcNetoCanc
    wrkNetoTotal += calcMontoREFI
    wrkNetoTotal += manejo_5porc
    wrkNetoTotal -= 0  # dev Interes
    wrkNetoTotal -= 0  # dev Seguro
    if tipo_prestamo == "PREST AUTO":
       
        wrkNetoTotal += 291.90
    
    #print("wrkNetoTotal:",wrkNetoTotal)

    #print('manejo_5porc:', manejo_5porc)
    #print('wrkNetoTotal:', wrkNetoTotal)

    ##print("wrkNetoTotal =", wrkNetoTotal
    # Calcular 5% devolución de impuesto de seguro
    wrkDes5Porciento = 0
    # Evaluar 5% seguro REFI
    wrkFechaAnterior5 = datetime.datetime(2010, 6, 1)
    parimptoFechaSeguro1 = datetime.datetime(2010, 10, 9)
    wrkMonto21 = wrkDes5Porciento
    # Obtener el primer día hábil
    primerDiaHabil = tempPrimerDiaHabil
    if primerDiaHabil >= wrkFechaAnterior5 and primerDiaHabil <= parimptoFechaSeguro1:
        wrkMonto21 *= 0.05
    else:
        wrkMonto21 *= 0.07
    
    wrkNetoTotal -= wrkMonto21
    wrkNetoTotal += parmgralComisionPers
    wrkNetoTotal += comisionVendedor
    #print("comisionVendedor =", comisionVendedor, "parmgralComisionPers =", parmgralComisionPers)
    #print("wrkNetoTotal =", wrkNetoTotal)
    
    wrkNetoTotal2 = wrkNetoTotal
    auxP = tipopagoPeriocidad
    auxW = 0
    wrkcontador = 0
    auxL = 0.000102
    # se adiciona gasto de desc. para los jubilados 620.. (1.5)
    auxJ = 0
    if patrono == 620 and tipo_prestamo != "LEASING":
        auxJ = calcMontoLetra
        auxJ = (auxJ * auxP) * 1.5 / 100
    
    auxX = calcTasaInteres
    auxX += 1
    auxX = pow(auxX, (1 / 12))
    wrkNumeric5_7 = auxX
   # print("auxX =", auxX)
    auxX = wrkNumeric5_7
    auxX = round(auxX, 7)
    #print("auxX =", auxX)
    auxX -= 1
    auxX = round(auxX, 7)
    
    auxV = wrkNum7_2
    auxV = auxV / plazoPago
    auxV = round(auxV, 13)
    #print("auxV =", auxV)
    auxX = round(auxX, 7)

    calcInicioPago = cotFechaInicioPago
    
    #calcFechaPromeCK =calcFechaPromeCK
    
    #CICLO CALCULO RENTA
    contador =0
    auxRepetir = True
    while auxRepetir:
        auxK = 0
        contador = contador +1
        auxW += 1
        wrkMes = fechaInicioPago.month
        wrkNum3 = wrkMes
        auxG = wrkNum3
        ##print("auxG =", auxG)
        auxF = plazoPago
        auxO = 0

        #LABEL - CICLO DE DICIEMBRE
        auxB = plazoInteres
        wrkMonto = 0
        wrkFecha2 = params['fechaCalculo']
        
        wrkFecha2 = calcFechaPromeCK
        #wrkfecha2 = 2024 december 01
        wrkFecha2 = datetime.datetime(2024, 12, 1)
        ##print("wrkFecha2 =", wrkFecha2)
         # Ensure wrkFecha2 is a datetime object
        if isinstance(wrkFecha2, str):
            wrkFecha2 = datetime.datetime.strptime(wrkFecha2, "%Y-%m-%d")

        
        wrkFecha2 += datetime.timedelta(days=1)
        ##print("wrkFecha2 =", wrkFecha2)
        

        wrkFechaMesYear1 = wrkFecha2
        wrkFechaMesYear2 = calcInicioPago

        auxT = (wrkFechaMesYear1.year - wrkFechaMesYear2.year) * 12 + wrkFechaMesYear1.month - wrkFechaMesYear2.month
        ##print("auxT =", auxT)
        if sobresaldo == "N":
            pass

        if auxT <= 0:
            auxT = 1

        if sobresaldo == "Y":
            auxB = auxB + auxT - 1

        #print("auxq:", auxQ)
        auxq_decimal = Decimal(str(auxQ))
        wrkNum9_2 = auxq_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        wrkNum9_2 = float(wrkNum9_2)  # Convert back to float

        #print("wrkNum9_2:",wrkNum9_2)
        auxQ = wrkNum9_2
        wrkNum9_2 = round(auxV,2)
        #print("wrkNum9_2:",wrkNum9_2)
        auxV = wrkNum9_2
        auxV = round(auxV, 2)
        auxQ = round(auxQ, 3)
        
        ##print("auxQ =", auxQ)
        
        auxQI = 0
        auxE = round(calcMontoLetra,2)
        auxE *= auxP
        auxE -= auxQ
        auxE -= auxV
        auxE -= auxJ
        auxS = auxE
        #print("auxS =", auxS)
        for auxA in range(auxT, auxB+1):
            if plazoPago == 1:
                if auxA == auxB:
                    pass
                else:
                    pass

            auxQI += 1
            auxE = auxS
            auxD = 1 + auxX
            auxZ = auxD
            auxH = auxX
            
            
            
            wrkAlpha4 = auxB
            if pagadiciembre1 == "Y" or wrkNum3 != 12:
                auxR = auxA
                auxD = pow(auxD, auxR)
                auxE = auxE / auxD
            else:
                auxE = 0
           
            rentableSecuencia = auxA
            rentableMes = wrkNum3
            rentableValor = round(auxE, 2)

            if wrkNum3 != 12:
                wrkNum3 += 1
            else:
                wrkNum3 = 1

            wrkMonto += auxE
            wrkMonto = round(wrkMonto, 2)
            #print('wrkMonto:',wrkMonto,"auxA:",auxA,"auxE:",auxE,"auxw:",auxW)

            
            

        
        wrkCredito5 = wrkDebito
        wrkDebito = wrkMonto
        wrkDebito = wrkDebito - wrkNetoTotal
        wrkDebito = round(wrkDebito, 2)
        #print("wrkDebito =", wrkDebito)
        
        

        wrkCredito = auxW

        if auxW == 99999:
            #print("auxW == 99999",auxW)
            return
        
        if calcMonto2 <= 100000:
            wrkIG = -0.10
        else:
            wrkIG = -0.30

        if calcMonto2 > 100000:
            wrkIG = -1
        
        #print("wrkdebito:",wrkDebito,"0.01:",0.01)
        if wrkDebito < 0.01:
            #print("wrkDebito < wrkIG",wrkDebito,"<",wrkIG,wrkDebito<wrkIG,"auxW:",auxW)
            if wrkDebito < wrkIG:
                auxM = 0.000001
                auxL = 0.00000001
                auxX -= auxM
                auxX = round(auxX, 7)
                auxRepetir = True
                auxFlagNegativo = True
                #print("TT - auxX =", auxX)
            else:
                #print("TF - auxX =", auxX)
                auxRepetir = False
        else:  
            auxX += auxL
            auxX = round(auxX, 7)
            #print("F - auxX =", auxX,"auxW:",auxW)
            auxRepetir = True
            auxFlagNegativo = False
            if auxW == 999:
                auxRepetir = False

    
        '''
        if wrkDebito <= 0.3:
            wrkDebito = 0
            auxRepetir = False
        '''

    #FIN CICLO CALCULO RENTA
    #print('wrkd:',wrkDebito,'auxH:',auxH)
    wrkCredito2 = wrkDebito
    wrk1110 = auxH
    wrkRentaMensual = auxH
    
    auxY = auxH
    auxY = auxY * 100
    
    #print("auxH =", auxH)
    #print("auxY =", auxY)
    calcRentabilidad = auxY
    #calcRentabilidad = round(calcRentabilidad * 100 / 10000, 4)
    #print("calcRentabilidad =", calcRentabilidad)


    ##print("calcRentabilidad =", calcRentabilidad)
    auxU = auxY * 12
    #print("auxU =", auxU)

    calcRentaAnual = auxU
    calcRentaAnual = round(calcRentaAnual * 100 / 10000, 4)
    r1 = calcRentaAnual
    #r1 = round(r1, 2)

    print("R1 =", r1)

    #calculo para la tasa efectiva, diferenciarla de la r1
    TasaEfectiva = rentabilidadEfectiva(calcMonto2,sobresaldo,wrkMontoFECI,wrkNum7_2,plazoPago,calcMontoNetoBruto,calcMontoTimbres,calcMontoNotaria,tipopagoPeriocidad,patrono,tipo_prestamo,calcTasaInteres,fechaInicioPago,plazoInteres,fechaCalculo,calcMontoLetra,calcInicioPago,tempPrimerDiaHabil,params)
    #TasaEfectiva=round(TasaEfectiva,2)
    print("TasaEfectiva =", TasaEfectiva)
    return TasaEfectiva, r1

