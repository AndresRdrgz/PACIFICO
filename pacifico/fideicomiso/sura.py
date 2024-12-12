
def cotizacionSeguroAuto():

    marca = "KIA"
    modelo = "SPORTAGE"
    year = 2019
    valor = 20000
    yearsFinanciamiento = 1


    subTotal = 608.09
    impuestos = subTotal * 0.06
    total = subTotal + impuestos
    totalFinanciamiento = total * yearsFinanciamiento
    pagos12 = totalFinanciamiento / 12
    pagos12 =round(pagos12, 2)

    print("Total: ", total)
    print("Total Financiamiento: ", totalFinanciamiento)
    print("Pagos 12: ", pagos12)


cotizacionSeguroAuto()