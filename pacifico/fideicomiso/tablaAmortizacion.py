import datetime

def calculoInteres_F(wrkSaldoAnterior, tasaInteres, wrkDiasCalc):
    auxM = wrkSaldoAnterior
    auxN = tasaInteres
    auxO = wrkDiasCalc
    
    auxX = (((auxM * auxN) / 360) * auxO)
    auxX = round(auxX, 2)
    
    return auxX

def calculoFECI_F(calcLogic, wrkSaldoAnterior, auxMonto2, i, calcsobtFechaVenc, calcsobtFechaFin, auxLI, auxL, jubilado, wrkDiasEnteros2):
    tasaFeci = 1 / 100
    
    if calcLogic == "Y":
        return 0
    else:
        if auxMonto2 > 5000 and jubilado == "NO":
            auxM = wrkSaldoAnterior
            auxN = tasaFeci

            if i == 1:
                dias = (calcsobtFechaFin.date() - calcsobtFechaVenc).days
                auxH = dias + 1
                
                
            else:
                if i == auxL and auxLI == 2:
                    auxH = 15
                else:
                    dias = (calcsobtFechaFin - calcsobtFechaVenc).days
                    auxH = dias + 1

            if i == 1:
                auxH = wrkDiasEnteros2
            else:
                auxH = 30

            auxX = (((auxM * auxN) / 360) * auxH)
            calcsobtMontoFECI = round(auxX, 2)
        else:
            calcsobtMontoFECI = 0

        #print("calcsobtMontoFECI: ", calcsobtMontoFECI)
    
        return calcsobtMontoFECI

def calculoCapitalPagar_F(auxLI, auxXI, auxL, wrkMontoLetra, calcsobtMontoSeguro, calcsobtMontoFECI, calcsobtMontoInteres, calcsobtMontoCapital):
            calcsobtInteresPend = 0

            if auxLI == 2:
                if auxXI == 1 or auxXI == auxL:
                    wrkMontoLetra = wrkMontoLetra / 2

            wrkM2 = 0
            wrkM4 = 0
            wrkMontoLetra = round(wrkMontoLetra, 2)
            wrkSaldoCapital = wrkMontoLetra
            wrkSaldoCapital = wrkSaldoCapital - wrkM2 - calcsobtMontoSeguro
           
           
            if wrkSaldoCapital < 0:
                calcsobtSeguroPend = calcsobtMontoSeguro + wrkM2 - calcsobtMontoSeguro
                wrkM2 = calcsobtSeguroPend
                calcsobtMontoSeguro = wrkMontoLetra
                calcsobtMontoFECI = 0
                calcsobtMontoInteres = 0
                calcsobtMontoCapital = 0
                wrkSaldoCapital = 0
            else:
                calcsobtMontoSeguro = calcsobtMontoSeguro + wrkM2
                wrkM2 = 0

            #Restar FECI de la letra
            wrkM = wrkSaldoCapital
            wrkSaldoCapital = wrkSaldoCapital - wrkM4 - calcsobtMontoFECI
            

            if wrkSaldoCapital < 0:
                calcsobtFECIPend = calcsobtMontoFECI + wrkM4 - wrkM
                wrkM4 = calcsobtFECIPend
                calcsobtMontoFECI = wrkM
                calcsobtMontoInteres = 0
                calcsobtMontoCapital = 0
                wrkSaldoCapital = 0
            else:
                calcsobtMontoFECI = calcsobtMontoFECI + wrkM4
                wrkM4 = 0

            #Restar interes de la letra
            wrkM3 = 0
            wrkM = wrkSaldoCapital
            wrkSaldoCapital = wrkSaldoCapital - wrkM3 - calcsobtMontoInteres
            wrkSaldoCapital = round(wrkSaldoCapital, 2)

            if wrkSaldoCapital < 0:
                calcsobtInteresPend = calcsobtMontoInteres + wrkM3 - wrkM
                calcsobtInteresPend = round(calcsobtInteresPend, 2)
                wrkM3 = calcsobtInteresPend
                calcsobtMontoInteres = wrkM
                calcsobtMontoCapital = 0
                wrkSaldoCapital = 0
            else:
                calcsobtMontoInteres = calcsobtMontoInteres + wrkM3
                wrkM3 = 0

            calcsobtMontoSeguro = round(calcsobtMontoSeguro, 2)
            calcsobtMontoFECI = round(calcsobtMontoFECI, 2)
            calcsobtMontoInteres = round(calcsobtMontoInteres, 2)
            wrkSaldoCapital = round(wrkSaldoCapital, 2)
            calcsobtMontoCapital = round(calcsobtMontoCapital, 2)
            calcsobtInteresPend = round(calcsobtInteresPend, 2)
            wrkM = round(wrkM, 2)

            return calcsobtMontoSeguro,calcsobtMontoFECI,calcsobtMontoInteres, wrkSaldoCapital,calcsobtMontoCapital, calcsobtInteresPend, wrkM

def verificaDiferencia_F(wrkMontoLetra,wrkDiferencia):
    if wrkMontoLetra is None:
        auxL = 400
    else:
        auxL = wrkMontoLetra

    if wrkDiferencia is None:
        auxD = 10
    else:
        auxD = wrkDiferencia

    auxP = (auxD * 100) / auxL

    if auxP > 0.5:
        auxD = (auxL * 0.5) / 100

    auxD = round(auxD, 2)
    return auxD



def tablaAmortizacion(params):
    # PASE DE PARAMETROS
    #print(params)
    auxMonto2 = params['auxMonto2']
    auxPlazoPago = params['auxPlazoPago']
    auxPlazoInteres = auxPlazoPago
    cotTasaInteres = params['calcTasaInteres']
    auxA_seguro = params['totalSeguro']
    totalSeguro = params['totalSeguro']
    wrkMontoLetra = params['wrkMontoLetra']
    seguroAndres = params['seguroAdicional']
    jubilado = params['jubilado']

    #wrkMontoLetra = 276.38
    #-------
    #print("jubi: ", jubilado,"cotTasaInteres",cotTasaInteres)
    auxRecrear = True
    auxAndres = 1
    iteration_data = []
    #while auxRecrear = true
    while auxRecrear == True:
        auxRecrear = False
        #print("auxAndres: ", auxAndres)
        auxAndres += 1
        if auxAndres > 999:
            return tablaTotalPagos, tablaTotalSeguro, tablaTotalFeci, tablaTotalInteres, tablaTotalMontoCapital, wrkMontoLetra, wrkLetraSeguro, iteration_data
        pagaDiciembre = "Y"
        wrkDiasCalcAnt =0
        wrkSaldo13 = 0
        wrkMontoNetoBruto = auxMonto2
        wrkValorSumar = 0
        wrkValorSumar2 = -10
        cantidadBol = 0
        parametrMesesPromoc = 1
        wrkfechaCalculo_init = datetime.datetime.now()
        wrkfechaCalculo = wrkfechaCalculo_init.date()
        parametrValidezCL = 30
        calcsobtSecuencia = 1
        wrkSaldoInteresAnt = 0
        wrkSaldoFeciAnt=0
        if jubilado == "NO":
            wrkLogic5 = "NO"
        else:
            wrkLogic5 = "SI"
        wrkSaldoSeguro = 0
        wrkSaldoSeguro2 = 0
        wrkcredito3 = 0
        wrkMontoSeguroAnt = 0
        wrkMontoTotal2 = 0
        tablaTotalPagos = 0
        tablaTotalSeguro = 0
        tablaTotalFeci = 0
        tablaTotalInteres = 0
        tablaTotalMontoCapital = 0

        wrkMontoLetraOfici = wrkMontoLetra
        #print("wrkMontoLetraOfici: ", wrkMontoLetraOfici,wrkMontoLetraOfici/2," + 0.001")
        wrkMontoLetraOfici = round(wrkMontoLetraOfici / 2 + 0.001, 2) * 2
        print("wrkMontoLetraOfici: ", wrkMontoLetraOfici)
       
        
        
        auxL = auxPlazoInteres
        auxXI = 0
        
        #SALDO ANTERIOR IGUAL A MONTO AMORTIZAR
        wrkSaldoAnterior = wrkMontoNetoBruto

        auxZ = seguroAndres    


        if pagaDiciembre == "Y":
            auxD = auxPlazoPago
        else:
            auxD = auxPlazoInteres
        
        auxD = auxD + auxZ

        #CALCULO DEL SEGURO ADICIONAL
        auxA = auxA_seguro
        auxB = 0    # VERIFICAR
        auxS = wrkSaldo13
        print("auxA: ", auxA, "auxB: ", auxB, "auxS: ", auxS)
       

        if auxB != auxD:
            auxB = auxD - auxB
            auxC = (auxA / auxB)
            auxC = round(auxC, 2)
            auxT = (auxS / auxB)
            wrkSaldoSeguro = auxC

            wrkSaldoSeguro = round(wrkSaldoSeguro, 2)
            wrkCredito2 = auxT
            wrkMontoTotal = wrkSaldoSeguro

            wrkMontoTotal = wrkMontoTotal * auxB
            wrkMontoTotal = round(wrkMontoTotal, 2)
           
            wrkMontoTotal13 = wrkCredito2
            wrkSaldoSeguro3 = 0
            wrkMontoTotal13 = wrkMontoTotal13 * auxB

            if totalSeguro != wrkMontoTotal:
                wrkSaldoSeguro3 = totalSeguro
                wrkSaldoSeguro3 = wrkSaldoSeguro3 - wrkMontoTotal
                wrkSaldoSeguro3 = round(wrkSaldoSeguro3, 2)

            if wrkSaldo13 != wrkMontoTotal13:
                wrkCredito3 = wrkSaldo13
                wrkCredito3 = wrkCredito3 - wrkMontoTotal13

            wrkPD = wrkSaldoSeguro
            wrkPD = wrkPD * auxZ
        else:
            wrkSaldoSeguro = 0
            wrkMontoTotal = 0
            wrkSaldoSeguro3 = 0
            wrkSaldo13 = 0
            wrkMontoTotal13 = 0
            wrkCredito3 = 0
        
        # GENERACION DE DISTRIBUCION DE PAGO
        if cantidadBol == 0:
            cantidadBol = parametrMesesPromoc
        
        if wrkfechaCalculo == "":
            fechaProemsaCK = ""
            cotFechaInicioPago = ""
        else:
            fechaProemsaCK = wrkfechaCalculo
            cotFechaInicioPago = wrkfechaCalculo
        
       
        wrkDiasenteros = 30
        wrkDiasenteros = wrkDiasenteros * cantidadBol
        wrkDiasEnteros2 = wrkDiasenteros
        wrkDiasEnteros2 = wrkDiasEnteros2 + 15
        

        fechaProemsaCK = fechaProemsaCK + datetime.timedelta(days=1)
        cotFechaInicioPago = cotFechaInicioPago + datetime.timedelta(days=wrkDiasenteros)
        cotFechaInicioPago = cotFechaInicioPago + datetime.timedelta(days=1)
       
        fechaValidez = fechaProemsaCK + datetime.timedelta(days=parametrValidezCL)
        inicioPago = cotFechaInicioPago

        wrkDia = cotFechaInicioPago.day
        
        auxLI = 0

        for i in range(1, auxL + 1):
            auxXI = auxXI + 1
            calcsobtSecuencia = auxXI

            if (i == 1):
                wrkFechaFICI = fechaProemsaCK
                wrkfecha = cotFechaInicioPago
                wrkDiasTrans = (wrkfecha - wrkFechaFICI).days
                #print("wrkDiasTrans: ", wrkDiasTrans)
               
            else:
                wrkfecha = wrkfecha + datetime.timedelta(days=30)

            if (auxXI == 1):
                calcsobtFechaVenc = fechaProemsaCK
                calcsobtFechaFin = cotFechaInicioPago
            else:
                calcsobtFechaVenc = wrkfechaCalculo
                calcsobtFechaFin = calcsobtFechaVenc
                #print("calcsobtFechaVenc: ", calcsobtFechaVenc, "calcsobtFechaFin: ", calcsobtFechaFin)

            #print("calcsobtFechaVenc: ", calcsobtFechaVenc, "calcsobtFechaFin: ", calcsobtFechaFin)
            wrkMes = calcsobtFechaFin.month
            
            if (auxXI == auxL or auxXI == 1):
                fecha1 = calcsobtFechaFin
                wrkDia = calcsobtFechaFin.day
                if 1 <= wrkDia <= 5:
                    calcsobtFechaFin = datetime.datetime(calcsobtFechaFin.year, calcsobtFechaFin.month, 5)
                elif 6 <= wrkDia <= 20:
                    calcsobtFechaFin = datetime.datetime(calcsobtFechaFin.year, calcsobtFechaFin.month, 20)
                else:
                    calcsobtFechaFin = datetime.datetime(calcsobtFechaFin.year, calcsobtFechaFin.month + 1, 5)

                if auxXI == auxL:
                    calcsobtFechaFin = calcsobtFechaFin + datetime.timedelta(days=30)
                    calcsobtFechaVenc = calcsobtFechaFin
            else:
                            
                
                calcsobtFechaFin = calcsobtFechaFin + datetime.timedelta(days=30)
                #print("calcsobtFechaFin: ", calcsobtFechaFin)
                #calcsobtFechaFin = calcsobtFechaFin - datetime.timedelta(days=1)
            
            calcsobtFechaFin = calcsobtFechaFin
            #print("calcsobtFechaFin: ", calcsobtFechaFin)
            
            wrkfecha2 = calcsobtFechaVenc
            wrkfechaCalculo = calcsobtFechaFin
            wrkfechaCalculo = wrkfechaCalculo + datetime.timedelta(days=1)
            
            calcsobtSaldoAnter = wrkSaldoAnterior
            #usar como base

            if (auxXI == 1):
                cotFechaInicioPago = calcsobtFechaFin
                wrkDiasTrans = wrkDiasEnteros2
                wrkDiasCalc = wrkDiasEnteros2
            else:
                wrkDiasTrans = 30
                wrkDiasCalc = 30
            
            calcsobtDiasCalc = wrkDiasCalc
            if wrkDiasCalcAnt == 0:
                pass  # T
            else:
                calcsobtDiasCalc = calcsobtDiasCalc + wrkDiasCalcAnt
                wrkDiasCalcAnt = 0

            #CALCULO DE INTERES
            calcsobtMontoInteres = calculoInteres_F(wrkSaldoAnterior,cotTasaInteres,wrkDiasCalc)

            #print("WrksaldoAnterior: ", wrkSaldoAnterior, "cotTasaInteres: ", cotTasaInteres, "wrkDiasCalc: ", wrkDiasCalc, "calcsobtMontoInteres: ", calcsobtMontoInteres)
            if wrkSaldoInteresAnt == 0:
                pass  # T
            else:
                calcsobtMontoInteres = calcsobtMontoInteres + wrkSaldoInteresAnt
                wrkSaldoInteresAnt = 0
            
            #CALCULO DEL FECI
            calcsobtMontoFECI = 0
            if wrkLogic5 == "SI":
                calcLogic = "Y"
            else:
                calcLogic = "N"

            
            jubilado = wrkLogic5

            if calcLogic == "Y":
                pass
            else:
                if(auxMonto2 > 5000 and jubilado == "NO"):
                    calcsobtMontoFECI= calculoFECI_F(calcLogic,wrkSaldoAnterior,auxMonto2,i,calcsobtFechaVenc,calcsobtFechaFin,auxLI,auxL,wrkLogic5,wrkDiasEnteros2)
                else:
                    calcsobtMontoFECI = 0
            
            #print("calcsobtMontoInteres",calcsobtMontoInteres,"calcsobtmontoFECI: ", calcsobtMontoFECI)
            if wrkSaldoFeciAnt == 0:
                pass
            else:
                calcsobtMontoFECI = calcsobtMontoFECI + wrkSaldoFeciAnt
                wrkSaldoFeciAnt = 0
            
            #MONTO SEGURO A LA TABLA
            if(auxLI == 2):
                auxB = auxB +1

            if (i == auxB):
                wrkSaldoSeguro = wrkSaldoSeguro + wrkSaldoSeguro3
                wrkSaldoSeguro = round(wrkSaldoSeguro, 2)
                wrkSaldoSeguro3 = 0
            
            calcsobtMontoSeguro = wrkSaldoSeguro
            calcsobtMontoSeguro = round(calcsobtMontoSeguro, 2)

            if (i ==auxB):
                wrkSaldo13 = wrkSaldo13 + wrkcredito3
                wrkCredito3 = 0
            
            calcsobtMontoSeguro2 = 0
            calcMesesSegPago = 0
            wrkSaldoSeguro4 = 0
            if(wrkSaldoSeguro2==0):
                pass
            else:
                calcsobtMontoSeguro = calcsobtMontoSeguro +wrkSaldoSeguro2
                wrkSaldoSeguro2 = 0
            
            if(wrkSaldoSeguro4 == 0):
                calcsobtMontoSeguro2 = calcsobtMontoSeguro2 + wrkSaldoSeguro4
                wrkSaldoSeguro4 =0
            
            if(auxLI == 2):
                
                if(auxXI == 1 or auxXI == auxL):
                    calcsobtMontoSeguro = wrkSaldoSeguro
                    calcsobtMontoSeguro = calcsobtMontoSeguro / 2
                    calcsobtMontoSeguro2 = calcsobtMontoSeguro2 / 2
                    auxQ = calcsobtMontoSeguro
                    auxQ = auxQ - wrkSaldoSeguro
                   
                    if(auxXI == auxL):
                        calcsobtMontoSeguro = calcsobtMontoSeguro - auxQ
                        calcsobtMontoSeguro2 = calcsobtMontoSeguro2 - auxQ
                if auxXI == auxL and calcMesesSegPago == 0:
                        calcsobtMontoSeguro = calcsobtMontoSeguro + wrkSaldoSeguro3
                auxBI = auxL
                auxBI = auxBI - calcMesesSegPago
                if auxXI > auxBI and calcMesesSegPago != 0:
                        calcsobtMontoSeguro = 0
                if auxBI == auxBI and calcMesesSegPago != 0:
                        calcsobtMontoSeguro = calcsobtMontoSeguro / 2
                        calcsobtMontoSeguro = calcsobtMontoSeguro + wrkSaldoSeguro3
                        auxQ = calcsobtMontoSeguro
                        auxQ = auxQ + auxQ
                        auxQ = auxQ - wrkSaldoSeguro
                        calcsobtMontoSeguro = calcsobtMontoSeguro + auxQ
            
            wrkMontoSeguroAnt = wrkMontoSeguroAnt + calcsobtMontoSeguro
            wrkMontoSeguroAnt = round(wrkMontoSeguroAnt, 2)
            
            #Suma si se trata de la primera letra
            if(i==1):
                #print("calcsobtMontoSeguro: ",calcsobtMontoSeguro, "wrkpd: ", wrkPD)
                calcsobtMontoSeguro=calcsobtMontoSeguro + wrkPD
                
            
            wrkIndicadorFracc = ""

            pagaDiciembre2 = "N"  # Example value, replace with actual logic
            #print("wrkmes: ", wrkMes, "pagaDiciembre2: ", pagaDiciembre2, "wrkIndicadorFracc: ", wrkIndicadorFracc)
            if ((wrkMes == 12 and pagaDiciembre2 == "Y") or wrkIndicadorFracc == "Y"):
                wrkSaldoCapital = 0
                wrkSaldoInteresAnt = calcsobtMontoInteres
                wrkSaldoFeciAnt = calcsobtMontoFECI
                wrkSaldoSeguro2 = calcsobtMontoSeguro
                wrkSaldoSeguro4 = calcsobtMontoSeguro2
                wrkDiasCalcAnt = wrkDiasCalc
                calcsobtMontoInteres = 0
                calcsobtMontoFECI = 0
                calcsobtMontoSeguro = 0
                calcsobtMontoSeguro2 = 0
                calcsobtMontoLetra = 0
                

                if wrkIndicadorFracc == "Y":
                    wrkSaldoInteresAnt = 0
                
            else:
                calcsobtMontoCapital = 0
                calcsobtMontoSeguro,calcsobtMontoFECI,calcsobtMontoInteres, wrkSaldoCapital,calcsobtMontoCapital, calcsobtInteresPend, wrkM = calculoCapitalPagar_F(auxLI,auxXI,auxL,wrkMontoLetra,calcsobtMontoSeguro,calcsobtMontoFECI,calcsobtMontoInteres,calcsobtMontoCapital)

                calcsobtMontoLetra = wrkMontoLetra
                calcsobtMontoLetra = round(calcsobtMontoLetra, 2)
                calcsobtMontoLetra = calcsobtMontoLetra / 2
                calcsobtMontoLetra = round(calcsobtMontoLetra, 2)
            

                if (auxXI == 1 or auxXI == auxL):
                    wrkDia = inicioPago.day
                    calcsobtMontoLetra =calcsobtMontoLetra + calcsobtMontoLetra 
                else:
                    calcsobtMontoLetra = calcsobtMontoLetra + calcsobtMontoLetra

                wrkMontoLetra = wrkMontoLetraOfici
                calcsobtMontoLetra = wrkMontoLetra
                
               
            #desgose de seguro en la tabla
            wrkSaldoSeguro = round(wrkSaldoSeguro, 2)
            wrkMontoTotal2 = wrkMontoTotal2 + calcsobtMontoSeguro
            wrkMontoTotal2 = round(wrkMontoTotal2, 2)

            if (totalSeguro == wrkMontoTotal2):
                wrkSaldoSeguro = 0
            
            calcsobtMontoCapital = calcsobtMontoLetra - calcsobtMontoSeguro - calcsobtMontoFECI - calcsobtMontoInteres 
            calcsobtMontoCapital = round(calcsobtMontoCapital, 2)
            
            if (calcsobtMontoCapital == 0.01):
                calcsobtMontoCapital = 0
                calcsobtMontoInteres = round(calcsobtMontoInteres + 0.01, 2)
                wrkSaldoInteresAnt = round(wrkSaldoInteresAnt - 0.01, 2)


            if (wrkMes == 12 or wrkIndicadorFracc == "Y"):
                #T
                if pagaDiciembre == "Y":
                    #TT
                    calcsobtSaldo = wrkSaldoAnterior
                    calcsobtSaldo = calcsobtSaldo - calcsobtMontoCapital
                else:
                    #TF
                    calcsobtSaldo = wrkSaldoAnterior
                wrkIndicadorFracc = "N"
            else:
                #F
                calcsobtSaldo = wrkSaldoAnterior
                calcsobtSaldo = calcsobtSaldo - calcsobtMontoCapital
            
            #fase final
            calcsobtSaldo = round(calcsobtSaldo, 2)
            wrkSaldoAnterior = calcsobtSaldo
            wrkSaldoBruto = calcsobtSaldo
            wrkSaldoAnterior = round(wrkSaldoAnterior, 2)
            wrkSaldoBruto = round(wrkSaldoBruto, 2)
            
            if (i == auxL and auxLI != 2):
                if calcsobtSaldoAnter < wrkSaldoCapital:
                    wrkMontoRecrear = calcsobtSaldoAnter

                if totalSeguro == wrkMontoTotal2:
                    pass
                else:
                    wrkCredito2 = totalSeguro
                    wrkCredito2 = wrkCredito2 - wrkMontoTotal2
                    wrkCredito2 = round(wrkCredito2, 2)
                    calcsobtMontoSeguro = calcsobtMontoSeguro + wrkCredito2
                    calcsobtMontoSeguro = round(calcsobtMontoSeguro, 2)
            
            if(calcsobtMontoInteres<0):
                pass
            
            wrkSecuencia = calcsobtSecuencia
            wrkMontoLetra = wrkMontoLetraOfici
            #ajuste ultima letra
            if (i == auxL):
                calcsobtSaldo = 0
                calcsobtMontoCapital = calcsobtSaldoAnter
                calcsobtMontoInteres = calcsobtSaldoAnter
                calcsobtMontoInteres = calcsobtMontoInteres + calcsobtMontoSeguro
                calcsobtMontoInteres = calcsobtMontoInteres + calcsobtMontoFECI
                calcsobtMontoInteres = calcsobtMontoInteres - calcsobtMontoLetra
                calcsobtMontoInteres = calcsobtMontoInteres * (-1)
                calcsobtMontoInteres = round(calcsobtMontoInteres, 2)
            
            #FIN TABLA
             #GUARDAR LETRA SEGURO
            if(i==1):
                wrkLetraSeguro = calcsobtMontoSeguro
                wrkLetraSeguro = round(wrkLetraSeguro, 2)

            tablaTotalPagos += calcsobtMontoLetra
            tablaTotalSeguro += calcsobtMontoSeguro
            tablaTotalFeci += calcsobtMontoFECI
            tablaTotalInteres += calcsobtMontoInteres
            tablaTotalMontoCapital += calcsobtMontoCapital

            if(i==1):
                calcFechaInicio = calcsobtFechaFin
                calcFechaPromeCK = calcsobtFechaVenc

            #print("Secuencia: ", wrkSecuencia, "Saldo anterior",calcsobtSaldoAnter,"Monto Letra: ", calcsobtMontoLetra, "Monto Seguro: ", calcsobtMontoSeguro, "Monto FECI: ", calcsobtMontoFECI, "Monto Interes: ", calcsobtMontoInteres, "Monto Capital: ", calcsobtMontoCapital)
            iteration_data.append({
                'Secuencia': wrkSecuencia,
                'FechaVencimiento': calcsobtFechaVenc.strftime('%d/%m/%Y'),
                'FechaFin': calcsobtFechaFin.strftime('%d/%m/%Y'),
                'Saldoanterior': calcsobtSaldoAnter,
                'MontoLetra': calcsobtMontoLetra,
                'MontoSeguro': calcsobtMontoSeguro,
                'MontoFECI': calcsobtMontoFECI,
                'MontoInteres': calcsobtMontoInteres,
                'MontoCapital': calcsobtMontoCapital,
                'SaldoActual': calcsobtSaldo
            })

            

            wrkMontoLetra = wrkMontoLetraOfici
        
        #FIN DE LOOP
        #print(iteration_data)
        calcMontoLetra = wrkMontoLetra
        wrkMontoLetraOfici = wrkMontoLetra
        #print("wrkMontoLetraOfici: ", wrkMontoLetraOfici)

        #LABEL SALIDA A RECREAR F
        wrkMontoExceso = auxPlazoPago
        wrkMontoExceso = wrkMontoExceso * 0.02
       
        

        tablaTotalPagos = round(tablaTotalPagos, 2)
        tablaTotalSeguro = round(tablaTotalSeguro, 2)
        tablaTotalFeci = round(tablaTotalFeci, 2)
        tablaTotalInteres = round(tablaTotalInteres, 2)
        tablaTotalMontoCapital = round(tablaTotalMontoCapital, 2)
        wrkMontoLetra = round(wrkMontoLetra, 2)

        print("wrkMontoLetraOfici",wrkMontoLetraOfici,"wrkmontoexceso: ", wrkMontoExceso,"wrkSaldoBruto",wrkSaldoBruto)
        #ojo - ajuste para minimizar el CR de colchon
        if wrkSaldoBruto < 0:
            wrkMontoBaloom = wrkSaldoBruto
            wrkMontoBaloom = wrkMontoBaloom * (-1)
            if wrkMontoBaloom > wrkMontoExceso:
                pass
            else:
                #print("Salida 1")
                return tablaTotalPagos, tablaTotalSeguro, tablaTotalFeci, tablaTotalInteres, tablaTotalMontoCapital, wrkMontoLetra, wrkLetraSeguro, iteration_data

        if wrkSaldoAnterior > 0:
            wrkValorSumar = 1
            wrkDiferencia = wrkSaldoAnterior
            wrkDiferencia = wrkDiferencia / auxL
            wrkDiferencia = wrkDiferencia / 2
            wrkDiferencia = round(wrkDiferencia, 2)
            wrkDiferencia = verificaDiferencia_F(wrkMontoLetra,wrkDiferencia)
            wrkDiferencia = round(wrkDiferencia, 2)
            if wrkDiferencia == 0:
                wrkDiferencia = 0.01
            wrkMontoLetra = wrkMontoLetra + wrkDiferencia
            wrkMontoLetra = round(wrkMontoLetra, 2)
            #print("wrkMontoLetra: ", wrkMontoLetra)
           
            
            auxRecrear = True
        
        
        if (wrkSaldoBruto < wrkValorSumar2):
            #print("ofi")
            wrkValorSumar2 -= wrkValorSumar
            wrkValorSumar = 0

            wrkMontoLetra = wrkMontoLetra - 0.02
            auxRecrear = True
        else:
            pass
        
       
            
        if(auxRecrear == False):
            #print("Salida 2")
            return tablaTotalPagos, tablaTotalSeguro, tablaTotalFeci, tablaTotalInteres, tablaTotalMontoCapital, wrkMontoLetra, wrkLetraSeguro, iteration_data
        #print("Salida 2")
        #return tablaTotalPagos, tablaTotalSeguro, tablaTotalFeci, tablaTotalInteres, tablaTotalMontoCapital, wrkMontoLetra

                
    


    
    #return tablaTotalPagos, tablaTotalSeguro, tablaTotalFeci, tablaTotalInteres, tablaTotalMontoCapital, wrkMontoLetra