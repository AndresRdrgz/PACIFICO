from .determinaMontoAmortizar import calculate_tasa_interes_mensual


def calculoMensualidadSobresaldo(cotPlazo,auxMonto2,cotTasaInteres):
    auxA = cotPlazo
    auxB = auxMonto2
    #print('cotTasaInteres = ',cotTasaInteres,'auxB = ',auxB)
    auxC = calculate_tasa_interes_mensual("NO", "Y",cotTasaInteres, auxB)

    auxC = auxC / 100
    #auxC = round(auxC,6)
    auxD = 1+auxC
    auxE = pow(auxD, auxA)
    #print("auxE = ",auxE," auxC = ",auxC," auxD = ",auxD," auxA = ",auxA)
    auxX = (auxB/((1-(1/auxE))/auxC))
    auxX = round(auxX,2)
    
    return auxX
