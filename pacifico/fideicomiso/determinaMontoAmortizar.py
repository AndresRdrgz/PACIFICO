from .seguro import auxBusquedaSeguro
def calculate_tasa_interes_mensual(wrk_logic5, sobresaldo, tasa_interes, monto2):
    tasa_feci = 1
    
    # Convert tasa_interes to percentage
    tasa_interes = tasa_interes * 100

    aux_a = tasa_interes

    if sobresaldo == "Y":
        if monto2 > 5000 and wrk_logic5 == "NO":
            # Add FECI
            aux_a = aux_a + tasa_feci

    aux_a = aux_a / 100
    aux_a = aux_a / 12
    aux_a = aux_a * 100

    tasa_interes_a = round(aux_a, 4)
    
    return tasa_interes_a
def calculate_tasa_interes_mensual_1(wrk_logic5, sobresaldo, tasa_interes, monto2):
    tasa_feci = 1
    monto2 = 0
    # Convert tasa_interes to percentage
    tasa_interes = tasa_interes * 100

    aux_a = tasa_interes

    if sobresaldo == "Y":
        if monto2 > 5000 and wrk_logic5 == "NO":
            # Add FECI
            aux_a = aux_a + tasa_feci

    aux_a = aux_a / 100
    aux_a = aux_a / 12
    aux_a = aux_a * 100

    tasa_interes_a = round(aux_a, 4)
    #print("Tasa interes mensual = ",tasa_interes_a)
    return tasa_interes_a

def determinar_monto_amortizar(cot_monto_prestamo, aux_notaria_gasto, comis_cierre, tipo_prestamo,codigoSeguro,edad,calcNetoCancelacion):
    
    #BUSCAR SEGURO
    tasa_bruta, sobretasa, tasa_real = auxBusquedaSeguro(codigoSeguro,edad)
    
    ##print(f"Tasa Bruta: {tasa_bruta}, Sobretasa: {sobretasa}, Tasa Real: {tasa_real}")
    tipo_prestamo = "PREST AUTO"
    aux_a = cot_monto_prestamo
    aux_b = calcNetoCancelacion
    #print("Monto a cancelar = ",aux_b)
    aux_h = 0
    aux_j = 0
    aux_k = 0
    
    aux_c = tasa_bruta
    aux_d = aux_notaria_gasto
    aux_m = 0
    aux_f = comis_cierre
    aux_i = 0
    aux_o = 0

    #print("Monto prestamo = ",aux_a,"calcNetoCancelacion = ",aux_b,"notaria = ",aux_d,"comis cierre = ",aux_f)

    # GASTO FIDEICOMISO EN EL FINANCIAMIENTO
    if tipo_prestamo == "PREST AUTO":
        aux_o = 291.90

    aux_c = aux_c / 100

    aux_l = ((aux_a + aux_b + aux_h) - (aux_j + aux_k + aux_i))

    aux_z = ((aux_l + aux_d) / (1 - aux_f))

    if tipo_prestamo == "PREST AUTO":
        aux_g = (aux_o * 100) / aux_z
        aux_f = comis_cierre * 100
        aux_f += aux_g
        aux_f = round(aux_f * 100) / 100
        comis_cierre = aux_f
        aux_f = comis_cierre / 100
        aux_z = ((aux_l + aux_d) / (1 - aux_f))

    aux_x = ((((aux_l + aux_d + aux_o) / (1 - aux_f)) * ((aux_c / 1000) * aux_m)) + aux_z)
    aux_x = round(aux_x * 100) / 100
    #print("Monto a amortizar = ",aux_x)

    return aux_l, aux_z, aux_x, comis_cierre/100, tasa_bruta,tasa_real
