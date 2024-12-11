def nivelEndeudamiento(resultado):
    print("------nivel de endeudamiento ------")
  
    
    
    
    totalIngresosAdicionales =resultado['horasExtrasMonto'] + resultado['primaMonto'] + resultado['bonosMonto'] + resultado['otrosMonto']
    totalIngresosAdicionales = round(totalIngresosAdicionales,2)
    print("Total de ingresos adicionales: ", totalIngresosAdicionales)
    totalDescuentoDirecto = resultado['siacapMonto'] + resultado['praaMonto'] + resultado['dirOtrosMonto1'] + resultado['dirOtrosMonto2'] + resultado['dirOtrosMonto3'] + resultado['dirOtrosMonto4']
    print("Total de descuentos directos: ", totalDescuentoDirecto)

    totalPagoVoluntario = resultado['pagoVoluntarioMonto1'] + resultado['pagoVoluntarioMonto2'] + resultado['pagoVoluntarioMonto3'] + resultado['pagoVoluntarioMonto4'] + resultado['pagoVoluntarioMonto5'] + resultado['pagoVoluntarioMonto6']
    print("Total de pagos voluntarios: ", totalPagoVoluntario)

    print(resultado)
    totalIngresosMensuales = resultado['salarioBaseMensual']
    totalIngresosMensualesCompleto = totalIngresosMensuales + totalIngresosAdicionales

    totalIngresosMensuales = round(totalIngresosMensuales,2)
    totalIngresosMensualesCompleto = round(totalIngresosMensualesCompleto,2)
    print("Total de ingresos mensuales: ", totalIngresosMensuales)

     
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

    #IMPUESTO SOBRE LA RENTAa
    if resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS', 'INDEPENDIENTE']:
        impuestoSobreLaRenta = 0
        impuestoSobreLaRentaCompleto = 0
    else:
        salarioAnual = totalIngresosMensuales * 13
        salarioAnualCompleto = totalIngresosMensualesCompleto * 13
        if salarioAnual < 11000:
            auxISR15 = 0
            auxISR25 = 0
            auxISR15Completo = 0
            auxISR25Completo = 0
        elif 11000 <= salarioAnual < 50000:
            auxISR15 = (salarioAnual - 11000) * 0.15
            auxISR25 = 0
            auxISR15Completo = (salarioAnualCompleto - 11000) * 0.15
            auxISR25Completo = 0

        else:
            auxISR15 = (50000 - 11000) * 0.15
            auxISR25 = (salarioAnual - 50000) * 0.25
            auxISR15Completo = (50000 - 11000) * 0.15
            auxISR25Completo = (salarioAnualCompleto - 50000) * 0.25


        impuestoSobreLaRentaAnual = auxISR15 + auxISR25
        impuestoSobreLaRenta = impuestoSobreLaRentaAnual / 13
        impuestoSobreLaRentaAnualCompleto = auxISR15Completo + auxISR25Completo
        impuestoSobreLaRentaCompleto = impuestoSobreLaRentaAnualCompleto / 13
        


    print("Impuesto Sobre la Renta: ", impuestoSobreLaRenta)


    totalDescuentosLegales = seguroSocial + seguroEducativo + impuestoSobreLaRenta
    totalDescuentosLegales = round(totalDescuentosLegales,2)
    totalDescuentosLegalesCompleto = seguroSocialCompleto + seguroEducativoCompleto + impuestoSobreLaRentaCompleto
    totalDescuentosLegalesCompleto = round(totalDescuentosLegalesCompleto,2)
    granTotalDescontado = totalDescuentoDirecto + totalPagoVoluntario + totalDescuentosLegales
    granTotalDescontado = round(granTotalDescontado,2)
    granTotalDescontadoCompleto = totalDescuentoDirecto + totalPagoVoluntario + totalDescuentosLegalesCompleto 
    print("Gran Total Descontado:", granTotalDescontado)
    
    salarioNetoActual = totalIngresosMensuales - granTotalDescontado
    salarioNetoActual = round(salarioNetoActual,2)
    salarioNetoActualCompleto = totalIngresosMensualesCompleto - granTotalDescontadoCompleto
    salarioNetoActualCompleto = round(salarioNetoActualCompleto,2)
    letraMensual = resultado['wrkLetraConSeguros']
    salarioNeto = salarioNetoActual - letraMensual
    salarioNeto = round(salarioNeto, 2)
    salarioNetoCompleto = salarioNetoActualCompleto - letraMensual
    salarioNetoCompleto = round(salarioNetoCompleto, 2)
    print("Cartera:", resultado['cartera'])
    
    # porcentajes
    porSalarioNetoActual = (salarioNetoActual / totalIngresosMensuales) * 100
    porLetraMensual = (letraMensual / totalIngresosMensuales) * 100
    porSalarioNeto = (salarioNeto / totalIngresosMensuales) * 100
    porSalarioNetoActualCompleto = (salarioNetoActualCompleto / totalIngresosMensualesCompleto) * 100
    porSalarioNetoCompleto = (salarioNetoCompleto / totalIngresosMensualesCompleto) * 100
    porLetraMensualCompleto = (letraMensual / totalIngresosMensualesCompleto) * 100
    print("Porcentaje Salario Neto Actual Completo:", porSalarioNetoActualCompleto)



    print("Porcentaje Salario Neto Actual:", porSalarioNetoActual)
    print("Porcentaje Letra Mensual:", porLetraMensual)
    print("Porcentaje Salario Neto:", porSalarioNeto)

    resultadoNivel = {
        'salarioNeto': salarioNeto,
        'porSalarioNeto': round(porSalarioNeto, 2),
        'totalDescuentoDirecto': totalDescuentoDirecto,
        'totalPagoVoluntario': totalPagoVoluntario,
        'salarioNetoActual': salarioNetoActual,
        'totalIngresosAdicionales': totalIngresosAdicionales,
        'totalIngresosMensuales': totalIngresosMensuales,
        'totalDescuentosLegales': totalDescuentosLegales,
        # NIVEL COMPLETO
        'salarioNetoCompleto': salarioNetoCompleto,
        'salarioNetoActualCompleto': salarioNetoActualCompleto,
        'porSalarioNetoCompleto': round(porSalarioNetoCompleto, 2),
        'totalDescuentosLegalesCompleto': totalDescuentosLegalesCompleto,
        'salarioNetoActualCompleto': salarioNetoActualCompleto,
        'totalIngresosMensualesCompleto': totalIngresosMensualesCompleto,
        
    }

    return resultadoNivel