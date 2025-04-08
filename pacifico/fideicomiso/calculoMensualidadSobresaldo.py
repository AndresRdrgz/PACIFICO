from .determinaMontoAmortizar import calculate_tasa_interes_mensual


def calculoMensualidadSobresaldo(cotPlazo,auxMonto2,cotTasaInteres):
    auxA = cotPlazo
    auxB = auxMonto2
    wrk_logic5 = "NO"
    
    auxC = calculate_tasa_interes_mensual(wrk_logic5, "Y",cotTasaInteres, auxB)
    #print(('cotTasaInteres = ',cotTasaInteres,'auxB = ',auxB,'auxC = ',auxC,"cotPlazo = ",cotPlazo)
    auxC = auxC / 100
    #auxC = round(auxC,6)
    auxD = 1+auxC
    auxE = pow(auxD, auxA)
    ##print(("auxE = ",auxE," auxC = ",auxC," auxD = ",auxD," auxA = ",auxA)
    auxX = (auxB/((1-(1/auxE))/auxC))
    auxX = round(auxX,2)
    
    #print(("Mensualidad = ",auxX)

    
    return auxX
