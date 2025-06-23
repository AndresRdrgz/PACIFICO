
def calcular_impuesto_sobre_la_renta(salario_anual):
    """
    Calcula el impuesto sobre la renta mensual basado en el salario anual.
    
    Args:
        salario_anual (float): Salario anual para el cálculo del impuesto
        
    Returns:
        float: Impuesto sobre la renta mensual
    """
    if salario_anual < 11000:
        aux_isr_15 = 0
        aux_isr_25 = 0
    elif 11000 <= salario_anual < 50000:
        aux_isr_15 = (salario_anual - 11000) * 0.15
        aux_isr_25 = 0
    else:
        aux_isr_15 = (50000 - 11000) * 0.15
        aux_isr_25 = (salario_anual - 50000) * 0.25
    
    impuesto_anual = aux_isr_15 + aux_isr_25
    return impuesto_anual / 13


def ImpuestoSobreLaRenta(resultado):
    # Legacy function - use calcular_impuesto_sobre_la_renta instead
    pass


def nivelEndeudamiento(resultado):
    #print("------nivel de endeudamiento ------")
    
    #print("Resultado recibido:", resultado)
    # print resultado with its field types
    for key, value in resultado.items():
        if value is None:
            resultado[key] = 0
        #print(f"{key}: {type(resultado[key]).__name__}")
    

    
    totalIngresosAdicionales =resultado['horasExtrasMonto'] + resultado['primaMonto'] + resultado['bonosMonto'] + resultado['otrosMonto']
    totalIngresosAdicionales = round(totalIngresosAdicionales,2)
    ##print("Total de ingresos adicionales: ", totalIngresosAdicionales)
    totalDescuentoDirecto = resultado['siacapMonto'] + resultado['praaMonto'] + resultado['dirOtrosMonto1'] + resultado['dirOtrosMonto2'] + resultado['dirOtrosMonto3'] + resultado['dirOtrosMonto4']
    ##print("Total de descuentos directos: ", totalDescuentoDirecto)

    totalPagoVoluntario = resultado['pagoVoluntarioMonto1'] + resultado['pagoVoluntarioMonto2'] + resultado['pagoVoluntarioMonto3'] + resultado['pagoVoluntarioMonto4'] + resultado['pagoVoluntarioMonto5'] + resultado['pagoVoluntarioMonto6']
    ##print("Total de pagos voluntarios: ", totalPagoVoluntario)

    ##print(resultado)
    #print("movOpcion: ", resultado.get('movOpcion'))
    # if 'movOpcion' is not in resultado or is None, set it to 'ingresar_manual'
    if 'movOpcion' not in resultado or resultado['movOpcion'] is None:
        resultado['movOpcion'] = 'ingresar_manual'

    
    totalIngresosMensuales = resultado['salarioBaseMensual']
    totalIngresosMensualesCompleto = totalIngresosMensuales + totalIngresosAdicionales

    totalIngresosMensuales = round(totalIngresosMensuales,2)
    totalIngresosMensualesCompleto = round(totalIngresosMensualesCompleto,2)
    ##print("Total de ingresos mensuales: ", totalIngresosMensuales)

     
     #SEGURO SOCIAL
    if resultado['cartera'] == 'INDEPENDIENTE':
        seguroSocial = 0
        seguroSocialCompleto = 0
    elif resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS']:
        seguroSocial = (totalIngresosMensuales * 6.75) / 100
        seguroSocialCompleto = (totalIngresosMensualesCompleto * 6.75) / 100
    else:
        seguroSocial = (totalIngresosMensuales * 9.75) / 100
        seguroSocialCompleto = (totalIngresosMensualesCompleto * 9.75) / 100

    print("Seguro Social: ", seguroSocial)

    #SEGURO EDUCATIVO
    if resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS', 'INDEPENDIENTE']:
        seguroEducativo = 0
        seguroEducativoCompleto = 0
    else:
        seguroEducativo = (totalIngresosMensuales * 1.25) / 100
        seguroEducativoCompleto = (totalIngresosMensualesCompleto * 1.25) / 100

    print("Seguro Educativo: ", seguroEducativo)

    #IMPUESTO SOBRE LA RENTA
    print("Impuesto sobre la renta - Cartera:", resultado['cartera'])
    if resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS', 'INDEPENDIENTE']:
        impuestoSobreLaRenta = 0
        impuestoSobreLaRentaCompleto = 0
    else:
        salarioAnual = totalIngresosMensuales * 13
        salarioAnualCompleto = totalIngresosMensualesCompleto * 13
        print("Salario Anual: ", salarioAnual, " - Salario Anual Completo: ", salarioAnualCompleto)
        
        # Calcular impuesto para salario base
        impuestoSobreLaRenta = calcular_impuesto_sobre_la_renta(salarioAnual)
        
        # Calcular impuesto para salario completo
        impuestoSobreLaRentaCompleto = calcular_impuesto_sobre_la_renta(salarioAnualCompleto)
        


    print("Impuesto Sobre la Renta: ", impuestoSobreLaRenta)
    print("Impuesto Sobre la Renta Completo: ", impuestoSobreLaRentaCompleto)


    totalDescuentosLegales = seguroSocial + seguroEducativo + impuestoSobreLaRenta
    totalDescuentosLegales = round(totalDescuentosLegales,2)
    totalDescuentosLegalesCompleto = seguroSocialCompleto + seguroEducativoCompleto + impuestoSobreLaRentaCompleto
    totalDescuentosLegalesCompleto = round(totalDescuentosLegalesCompleto,2)
    granTotalDescontado = totalDescuentoDirecto + totalPagoVoluntario + totalDescuentosLegales
    granTotalDescontado = round(granTotalDescontado,2)
    granTotalDescontadoCompleto = totalDescuentoDirecto + totalPagoVoluntario + totalDescuentosLegalesCompleto 
    ##print("Gran Total Descontado:", granTotalDescontado)
    
    salarioNetoActual = totalIngresosMensuales - granTotalDescontado
    salarioNetoActual = round(salarioNetoActual,2)
    salarioNetoActualCompleto = totalIngresosMensualesCompleto - granTotalDescontadoCompleto
    salarioNetoActualCompleto = round(salarioNetoActualCompleto,2)
    if resultado['tipoPrestamo'] == 'PERSONAL':
        if resultado['auxPeriocidad'] == 2:
            letraMensual = resultado['wrkLetraConSeguros'] * 2
        else:
            letraMensual = resultado['wrkLetraConSeguros']
    else:
        letraMensual = resultado['wrkLetraConSeguros']
       
    
    print("Salario Neto = ", salarioNetoActual, " - Letra Mensual = ", letraMensual)
    salarioNeto = salarioNetoActual - letraMensual
    salarioNeto = round(salarioNeto, 2)
    salarioNetoCompleto = salarioNetoActualCompleto - letraMensual
    salarioNetoCompleto = round(salarioNetoCompleto, 2)
    ##print("Cartera:", resultado['cartera'])
    
    # porcentajes
    try:
        porSalarioNetoActual = (salarioNetoActual / totalIngresosMensuales) * 100
    except ZeroDivisionError:
        porSalarioNetoActual = 0

    try:
        porLetraMensual = (letraMensual / totalIngresosMensuales) * 100
    except ZeroDivisionError:
        porLetraMensual = 0

    try:
        porSalarioNeto = (salarioNeto / totalIngresosMensuales) * 100
    except ZeroDivisionError:
        porSalarioNeto = 0

    try:
        porSalarioNetoActualCompleto = (salarioNetoActualCompleto / totalIngresosMensualesCompleto) * 100
    except ZeroDivisionError:
        porSalarioNetoActualCompleto = 0

    try:
        porSalarioNetoCompleto = (salarioNetoCompleto / totalIngresosMensualesCompleto) * 100
    except ZeroDivisionError:
        porSalarioNetoCompleto = 0

    ##print("Porcentaje Salario Neto Actual Completo:", porSalarioNetoActualCompleto)



    ##print("Porcentaje Salario Neto Actual:", porSalarioNetoActual)
    ##print("Porcentaje Letra Mensual:", porLetraMensual)
    ##print("Porcentaje Salario Neto:", porSalarioNeto)
    resultadoNivel = {
        'salarioNeto': round(salarioNeto, 2),
        'porSalarioNeto': round(porSalarioNeto, 2),
        'totalDescuentoDirecto': round(totalDescuentoDirecto, 2),
        'totalPagoVoluntario': round(totalPagoVoluntario, 2),
        'salarioNetoActual': round(salarioNetoActual, 2),
        'totalIngresosAdicionales': round(totalIngresosAdicionales, 2),
        'totalIngresosMensuales': round(totalIngresosMensuales, 2),
        'totalDescuentosLegales': round(totalDescuentosLegales, 2),
        # NIVEL COMPLETO
        'salarioNetoCompleto': round(salarioNetoCompleto, 2),
        'salarioNetoActualCompleto': round(salarioNetoActualCompleto, 2),
        'porSalarioNetoCompleto': round(porSalarioNetoCompleto, 2),
        'totalDescuentosLegalesCompleto': round(totalDescuentosLegalesCompleto, 2),
        'totalIngresosMensualesCompleto': round(totalIngresosMensualesCompleto, 2),
    }
    print("Resultado Nivel:", resultadoNivel)
    return resultadoNivel
