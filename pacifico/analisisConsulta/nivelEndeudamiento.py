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
    totalIngresosMensuales = resultado['salarioBaseMensual'] + totalIngresosAdicionales
    totalIngresosMensuales = round(totalIngresosMensuales,2)
    print("Total de ingresos mensuales: ", totalIngresosMensuales)

     
     #SEGURO SOCIAL
    if resultado['cartera'] == 'INDEPENDIENTE':
        seguroSocial = 0
    elif resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS']:
        seguroSocial = (totalIngresosMensuales * 6.75) / 100
    else:
        seguroSocial = (totalIngresosMensuales * 9.75) / 100

    print("Seguro Social: ", seguroSocial)

    #SEGURO EDUCATIVO
    if resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS', 'INDEPENDIENTE']:
        seguroEducativo = 0
    else:
        seguroEducativo = (totalIngresosMensuales * 1.25) / 100

    print("Seguro Educativo: ", seguroEducativo)

    #IMPUESTO SOBRE LA RENTAa
    if resultado['cartera'] in ['JUBILADO RIESGOS PROF. CSS', 'JUBILADO CONTRALORIA', 'JUBILADO DE LA ZONA', 'JUBILADO CSS', 'INDEPENDIENTE']:
        impuestoSobreLaRenta = 0
    else:
        salarioAnual = totalIngresosMensuales * 13
        if salarioAnual < 11000:
            auxISR15 = 0
            auxISR25 = 0
        elif 11000 <= salarioAnual < 50000:
            auxISR15 = (salarioAnual - 11000) * 0.15
            auxISR25 = 0
        else:
            auxISR15 = (50000 - 11000) * 0.15
            auxISR25 = (salarioAnual - 50000) * 0.25

        impuestoSobreLaRentaAnual = auxISR15 + auxISR25
        impuestoSobreLaRenta = impuestoSobreLaRentaAnual / 13

    print("Impuesto Sobre la Renta: ", impuestoSobreLaRenta)


    totalDescuentosLegales = seguroSocial + seguroEducativo + impuestoSobreLaRenta
    totalDescuentosLegales = round(totalDescuentosLegales,2)
    granTotalDescontado = totalDescuentoDirecto + totalPagoVoluntario + totalDescuentosLegales
    print("Gran Total Descontado:", granTotalDescontado)
    
    salarioNetoActual = totalIngresosMensuales - granTotalDescontado
    salarioNetoActual = round(salarioNetoActual,2)
    letraMensual = resultado['wrkLetraConSeguros']
    salarioNeto = salarioNetoActual - letraMensual
    salarioNeto = round(salarioNeto, 2)

    print("Cartera:", resultado['cartera'])
    
    # porcentajes
    porSalarioNetoActual = (salarioNetoActual / totalIngresosMensuales) * 100
    porLetraMensual = (letraMensual / totalIngresosMensuales) * 100
    porSalarioNeto = (salarioNeto / totalIngresosMensuales) * 100

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
    }

    return resultadoNivel