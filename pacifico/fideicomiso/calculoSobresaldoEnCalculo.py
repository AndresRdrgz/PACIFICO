import datetime

def calculoTimbres(comis_cierre,monto2):
    
    
    ###print(('comis_cierre:', comis_cierre, 'monto2:', monto2)
    sobresaldo = "Y"
    
    if comis_cierre == "":
        return

    aux_s = ""

    if sobresaldo == "N" and monto2 == "":
        # AGREGADO
        # T
        pass

    aux_a = float(monto2)
    aux_a = aux_a / 100
    first_decimal_digit = int((aux_a % 1) * 10)

    wrk_redondeo = round(aux_a)
    ###print(('wrk_redondeo:', wrk_redondeo,'aux_a:', aux_a)
    wrk_alpha16 = aux_a
    temp79 = ""

    wrk_decimal = ""

    aux_b = wrk_redondeo * 0.10
    aux_b = round(aux_b, 1)

    if wrk_decimal != "":
        aux_b += 0.10
    
    
    ##print(("monto2",monto2)
    ##print(('aux_b:', aux_b)
    
    #MODIFICACION ENERO 2025 CALCULO TIMBRES
    timbresAndres = (monto2 // 100) * 0.10
    ##print(('timbresAndres:', timbresAndres)
    integer_part = int(monto2 // 100)
    decimal_part = monto2 % 100
    ##print(('integer_part:', integer_part)
    ##print(('decimal_part:', decimal_part)
    ###print(('aux_b:', aux_b)
    timbres = integer_part * 0.10
    if decimal_part > 0:
        timbres += 0.10
    timbres = round(timbres, 2)
    aux_b = timbres
    ##print(('timbres:', timbres)
    return round(aux_b,2)

def calculo_servicio_descuento(params):
    servDesc = 0
    montoServDesc = 0
    edad = params['edad']
    sexo = params['sexo']
    jubilado = params['jubilado']
    patrono = params['patrono']
    selectDescuento = params['selectDescuento']
    porServDesc = params['porServDesc']
    edadJubFem = 55
    edadJubMas = 60
    auxA = 0
    auxB = 0
    montoLetra = params['wrkMontoLetra']
    noLetras = params['auxPeriocidad'] * params['auxPlazoPago']
    print('noLetras:', noLetras)


    if edad >= edadJubFem and sexo == "FEMENINO":
        return montoServDesc
    elif edad >= edadJubMas and sexo == "MASCULINO":
        return montoServDesc
    
    if jubilado != "NO":
        #METER TIPO DE JUB JCC AND JCS
        return montoServDesc
    
    if patrono != "9999":
        if selectDescuento == "Y":
           pass

    if porServDesc > 0:
        print('porServDesc:', porServDesc, 'montoLetra:', montoLetra, 'noLetras:', noLetras)
        auxA = noLetras * montoLetra
        auxb = porServDesc
        auxb = auxb / 100
        auxA = auxA * float(auxb)
        montoServDesc = auxA

    return montoServDesc
    

    
    #NO APLICA SERVICIO DE DESCUENTO SE GUARDA CALCULI PARA APLICAR COMO GASTO








   
    return None


def calculate_comision_manejo(sobresaldo, comis_cierre, monto2, monto1):
    aux_a = 0
    aux_f = 0
    aux_x = 0
    aux_b = 0
    monto_manejo_t = 0
    agregado = "N"

    #print(('sobresaldo:', sobresaldo, 'comis_cierre:', comis_cierre, 'monto2:', monto2, 'monto1:', monto1)

    if sobresaldo == "Y":
        aux_f = comis_cierre
        aux_a = monto2
        aux_x = aux_a * aux_f
        monto_manejo_t = aux_x
    else:
        aux_a = monto1
        aux_b = comis_cierre / 100
        aux_a = aux_a * aux_b
        monto_manejo_t = aux_a

    # CALCULO 5%
    if agregado == "Y":
        # Additional logic for "agregado" can be added here if needed
        pass
    
    return round(monto_manejo_t, 2)

def calculate_gasto_manejo(monto_manejo_t, sobresaldo, monto_serv_des, monto_timbres, tipo_prestamo):
    # Calculate initial monto_manejo_b
    porcentaje_manejo = 0.0654205
    
    monto_manejo_b = monto_manejo_t - monto_serv_des - monto_timbres
    if tipo_prestamo == "PREST AUTO":
        monto_manejo_b = monto_manejo_b - 291.90
    monto_manejo_b = round(monto_manejo_b, 2)
    
    if sobresaldo == "Y":
        wrk_monto21 = monto_manejo_b
        manejo_5porc = monto_manejo_b * porcentaje_manejo
        monto_manejo_b = monto_manejo_b - manejo_5porc
        wrk_monto20 = manejo_5porc + monto_manejo_b

        if wrk_monto20 != wrk_monto21:
            wrk_monto15 = wrk_monto21
            monto15 = wrk_monto15 - wrk_monto20
            monto_manejo_b = monto_manejo_b + wrk_monto15

    # Round manejo_5porc to 2 decimal places
    manejo_5porc = round(manejo_5porc, 2)
    return wrk_monto21, round(monto_manejo_b,2), manejo_5porc


def calculate_monto_obligacion(sobresaldo, tipo_prestamo, aux_monto_manejo_t, aux_notaria_gasto, aux_monto2):
    descontado = "N"  # Example value
    if descontado == "Y":
        # GOSUB MONTO1 PARA DESCONTADO
        pass

    if sobresaldo == "Y":
        aux_b = 0
        aux_c = 0
        aux_d = 0
        aux_e = 0
        aux_f = aux_monto_manejo_t
        aux_g = aux_notaria_gasto
        aux_i = aux_monto2
        aux_j = 0
        aux_o = 0

        if tipo_prestamo == "PREST AUTO":
            aux_o = 291.90

        aux_m = 0  # Assuming aux_m is 0 as per the provided logic

        aux_y = (aux_b + aux_c) - (aux_d + aux_e + aux_m)
        aux_x = aux_i - aux_f - aux_y - aux_g - aux_j - aux_o

        monto1 = aux_x

        return monto1

def calculoSobresaldoEnCalculo(plazo_pago,cotMontoPrestamo,calcTasaInteres,calcMonto2,calcComiCierre,calcMontoNotaria,params):

   # Example usage
    monto_manejo_t = calculate_comision_manejo("Y",calcComiCierre,calcMonto2,cotMontoPrestamo)
    #print(('monto_manejo_t:', monto_manejo_t)
    
    params['montoManejoT'] = monto_manejo_t
    sobresaldo = "Y"  # Example value
    montoServDesc = 0  #inicializando
    tipo_prestamo = params['tipoPrestamo']
    pagadiciembre1 = "Y"
    forma_pago = 1  # Example value

    #print((params)

    #calculo neto cancelacion
      

    #MONTO TIMBRES
    monto_timbres = calculoTimbres(calcComiCierre,calcMonto2)
    params['calcMontoTimbres'] = monto_timbres
    ###print((f"Monto Timbres: {monto_timbres}")

    #Servicio Descuneto PRESTAMO PERSONAL
    if tipo_prestamo == "PERSONAL":
        montoServDesc = calculo_servicio_descuento(params)
        montoServDesc =round(montoServDesc,2)
        params['montoServDesc'] = montoServDesc
        #print(('montoServDesc:', montoServDesc)
        
        ###print((f"Fecha Servicio Descuento: {fecha_servicio

    #print( ("servicio descuento fin",montoServDesc)
    
    #GASTO MANEJO
    wrk_monto21, monto_manejo_b, manejo_5porc = calculate_gasto_manejo(monto_manejo_t, sobresaldo, montoServDesc, monto_timbres,tipo_prestamo)
    ###print((f"wrkMonto21: {wrk_monto21}, Monto Manejo B: {monto_manejo_b}, Manejo 5%: {manejo_5porc}")
    params['monto_manejo_b'] = monto_manejo_b
    sobresaldo = "Y"  # Example value
    aux_notaria_gasto = calcMontoNotaria  # Example value
    aux_monto2 = calcMonto2 # Example value
    #MONTO OBLIGACION
    monto1 = calculate_monto_obligacion(sobresaldo, tipo_prestamo, monto_manejo_t, aux_notaria_gasto, aux_monto2)
    ###print((f"Monto1: {monto1}")
    params['manejo_5porc'] = manejo_5porc

    return params
