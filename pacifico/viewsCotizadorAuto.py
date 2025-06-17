from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import FideicomisoForm
from .fideicomiso.fideicomiso import generarFideicomiso3
from .analisisConsulta.nivelEndeudamiento import nivelEndeudamiento
import datetime
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import Cotizacion, UserProfile
import json
import logging
from .viewsFideicomiso.cotizadorFideicomiso import (
    convert_decimal_to_float,
    calculoInicial,
    prepResultado,
)


@login_required
def cotizadorPrestAuto(request, pk=None):
    resultado = None
    cotizacion = None
    print("Cotizacion Prestamo auto, pk:", pk)
    if pk:
        cotizacion = get_object_or_404(Cotizacion, pk=pk)
        resultado = prepResultado(cotizacion)



    if request.method == 'POST':
        form = FideicomisoForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            try:
                # Extract form data
                edad = form.cleaned_data['edad']
                sexo = form.cleaned_data['sexo']
                jubilado = form.cleaned_data['jubilado']
                nombreCliente = form.cleaned_data['nombreCliente']
                selectDescuento = form.cleaned_data['selectDescuento']
                cotMontoPrestamo = Decimal(form.cleaned_data['montoPrestamo'])
                calcTasaInteres = 10 / 100
                calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
                auxPlazoPago = form.cleaned_data['plazoPago']
                patrono = form.cleaned_data['patronoCodigo']
                print('patrono', patrono)
                aplicaPromocion = form.cleaned_data['aplicaPromocion']
                print('aplicaPromocion', aplicaPromocion)
                #if patrono is None: patrono = 9999
                if patrono is None: patrono = 9999

                sucursal = 13
                auxPeriocidad = 1
                forma_pago = 4
                #COLECTIVO DE CREDITO
                aseguradora = form.cleaned_data['aseguradora']
                #print('aseguradora', aseguradora)
                codigoSeguro = aseguradora.codigo
                r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
                comisionVendedor = form.cleaned_data['vendedorComision']
                #CAMPOS SEGURO AUTO
                financiaSeguro = form.cleaned_data['financiaSeguro']
                mesesFinanciaSeguro = form.cleaned_data['mesesFinanciaSeguro']
                montoanualSeguro = form.cleaned_data['montoanualSeguro']
                montoMensualSeguro = form.cleaned_data['montoMensualSeguro']
                cantPagosSeguro = form.cleaned_data['cantPagosSeguro']
                sucursal = form.cleaned_data['sucursal']
                selectDescuento = form.cleaned_data['selectDescuento']
                porServDesc = form.cleaned_data['porServDesc'] if form.cleaned_data['porServDesc'] is not None else 0
                pagaDiciembre = form.cleaned_data['pagaDiciembre']
                montoLetraSeguroAdelantado = mesesFinanciaSeguro * montoMensualSeguro
                montoLetraSeguroAdelantado = round(montoLetraSeguroAdelantado, 2)
                if montoLetraSeguroAdelantado is None:
                    montoLetraSeguroAdelantado = 0
                    

               
                #parse cotMontoPRestamo to float
                cotMontoPrestamo = float(cotMontoPrestamo)
                calcTasaInteres = float(calcTasaInteres)
                calcComiCierre = float(calcComiCierre)
                r_deseada = float(r_deseada)
                comisionVendedor = float(comisionVendedor)
                montoanualSeguro = float(montoanualSeguro)
                montoMensualSeguro = float(montoMensualSeguro)
                sucursal = int(sucursal)
                #print('Sucursal', sucursal)
                # Call the generarFideicomiso2 function
                params = {
                    'tipoPrestamo': 'PREST AUTO',
                    'edad': edad,
                    'sucursal': sucursal,
                    'sexo': sexo,
                    'jubilado': jubilado,
                    'cotMontoPrestamo': cotMontoPrestamo,
                    'calcTasaInteres': calcTasaInteres,
                    'calcComiCierre': calcComiCierre,
                    'auxPlazoPago': auxPlazoPago,
                    'patrono': patrono,
                    'sucursal': sucursal,
                    'auxPeriocidad': auxPeriocidad,
                    'forma_pago': forma_pago,
                    'codigoSeguro': codigoSeguro,
                    'fechaCalculo': datetime.datetime.now(),
                    'r_deseada': r_deseada,
                    'comisionVendedor': comisionVendedor,
                    'financiaSeguro': financiaSeguro,
                    'mesesFinanciaSeguro': mesesFinanciaSeguro,
                    'montoanualSeguro': montoanualSeguro,
                    'montoMensualSeguro': montoMensualSeguro,
                    'cantPagosSeguro': cantPagosSeguro,
                    'gastoFideicomiso': 291.90,
                    'aplicaPromocion': aplicaPromocion,
                    'selectDescuento': selectDescuento,
                    'porServDesc': porServDesc,
                    'pagaDiciembre': pagaDiciembre,

                }
                #print('RESULTADO PARAMETROS', params)
                resultado = generarFideicomiso3(params)
                
                print("--------finalizado---------")
                resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra']/2,2) * 2
                # print in ta table format reusltado

                resultado = calculoInicial(resultado,form, sexo, montoMensualSeguro, montoanualSeguro, auxPlazoPago, montoLetraSeguroAdelantado, aseguradora)


                 # Convert Decimal fields to floats
                resultado = convert_decimal_to_float(resultado)
                #print('resultado despues de funcion------', resultado)
                #CALCULO NIVEL DE ENDEUDAMIENTO - REAL
                resultadoNivel = nivelEndeudamiento(resultado)
                resultado['salarioNeto'] = resultadoNivel['salarioNeto']
                resultado['porSalarioNeto'] = resultadoNivel['porSalarioNeto']
                resultado['salarioNetoActual'] = resultadoNivel['salarioNetoActual']
                resultado['totalIngresosAdicionales'] = round(resultadoNivel['totalIngresosAdicionales'],2)
                resultado['totalIngresosMensuales'] = resultadoNivel['totalIngresosMensuales']
                resultado['totalDescuentoDirecto'] = resultadoNivel['totalDescuentoDirecto']
                resultado['totalPagoVoluntario'] = resultadoNivel['totalPagoVoluntario']
                resultado['totalDescuentosLegales'] = resultadoNivel['totalDescuentosLegales']
                #nivel de endeudamiento - completo
                resultado['totalIngresosMensualesCompleto'] = resultadoNivel['totalIngresosMensualesCompleto']
                resultado['totalDescuentosLegalesCompleto'] = resultadoNivel['totalDescuentosLegalesCompleto']
                resultado['salarioNetoActualCompleto'] = resultadoNivel['salarioNetoActualCompleto']
                resultado['salarioNetoCompleto'] = resultadoNivel['salarioNetoCompleto']
                resultado['porSalarioNetoCompleto'] = resultadoNivel['porSalarioNetoCompleto']
                #CODEUDOR - NIVEL DE ENDEUDAMIENTO
                
                if form.cleaned_data['aplicaCodeudor'] == "si":
                    print('aplica codeudor - CALCULAR NIVEL DE ENDEUDAMIENTO')
                    #resultadoNivelCodeudor = nivelEndeudamiento(codeudorResultado)

                
                #---------------------
                #save resultado['tasaEstimada'] in form instance
                form.instance.tasaEstimada = resultado['tasaEstimada']
                form.instance.tasaBruta = resultado['tasaBruta']
                form.instance.r1 = resultado['r1']
                form.instance.montoPrestamo = resultado['cotMontoPrestamo']
                form.instance.auxMonto2 = round(Decimal(resultado['auxMonto2']),2)
                form.instance.montoManejoT = resultado['montoManejoT']
                form.instance.monto_manejo_b = resultado['montoManejoB']
                #form.instance.apcPI = resultado['apcPI']
                form.instance.wrkMontoLetra = resultado['wrkMontoLetra']
                form.instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
                form.instance.wrkLetraSinSeguros = resultado['wrkLetraSinSeguros']
                form.instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
                form.instance.calcMontoNotaria = resultado['calcMontoNotaria']
                form.instance.calcMontoTimbres = resultado['calcMontoTimbres']
                form.instance.tablaTotalPagos = resultado['tablaTotalPagos']
                form.instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
                form.instance.tablaTotalFeci = resultado['tablaTotalFeci']
                form.instance.tablaTotalInteres = resultado['tablaTotalInteres']
                form.instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
                form.instance.manejo_5porc = resultado['manejo_5porc']
                form.instance.valorAuto = resultado['valorAuto']
                #form.instance.aseguradora = aseguradora
                
                #resultado nivel de endeuamiento - real                
                #resultado['lineaAuto'] = form.cleaned_data.get('lineaAuto', '-')
                #form.instance.lineaAuto = resultado['lineaAuto']
   
                form.instance.otrosMonto = resultado['otrosMonto']
                form.instance.bonosMonto = resultado['bonosMonto']
                form.instance.primaMonto = resultado['primaMonto']
                form.instance.salarioBaseMensual = resultado['salarioBaseMensual']
                form.instance.totalDescuentosLegales = resultado['totalDescuentosLegales']
                form.instance.totalDescuentoDirecto = resultado['totalDescuentoDirecto']
                form.instance.totalPagoVoluntario = resultado['totalPagoVoluntario']
                form.instance.salarioNetoActual = resultado['salarioNetoActual']
                form.instance.salarioNeto = resultado['salarioNeto']
                form.instance.porSalarioNeto = resultado['porSalarioNeto']
                form.instance.totalIngresosAdicionales = resultado['totalIngresosAdicionales']
                form.instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
                form.instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
                form.instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
                form.instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
                form.instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']
                form.instance.patrono = resultado['nombreEmpresa']
                form.instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                form.instance.tipoPrestamo = 'auto'
                
                #------SAFE-------
                try:
                    #print form fields
                    #print all form fields in form instan
                    for field in form.instance._meta.fields:
                        print(field.name, field.value_from_object(form.instance))

                    print("intentando guardar")
                    try:
                        form.save()
                        print("guardado")
                        numero_cotizacion = form.instance.NumeroCotizacion
                        resultado['numero_cotizacion'] = int(numero_cotizacion)
                        #print('NumeroCotizacion:', numero_cotizacion)
                        request.session['resultado'] = resultado
                        #print(request.user.username)
                        documentos_data = request.POST.get('documentos_data')
                        #--- GUARDADO DOCUMENTOS DEL CLIENTE -----
                        try:
                            if documentos_data:
                                documentos = json.loads(documentos_data)
                                processed_files = set()
                                file_counter = 0
                                for doc in documentos:
                                    documento_files = request.FILES.getlist(doc['documento'])
                                    if documento_files:
                                        unique_file_key = f"{doc['documento']}_{file_counter}"
                                        if unique_file_key not in processed_files:
                                            for documento_file in documento_files:
                                                print(f"Documento: {doc['documento']}", documento_file)
                                                
                                                # Save the document to the database
                                                CotizacionDocumento.objects.create(
                                                    cotizacion=form.instance,
                                                    tipo_documento=doc['tipoDocumento'],
                                                    documento=documento_file,
                                                    observaciones=doc['observaciones']
                                                )
                                                processed_files.add(unique_file_key)
                                                file_counter += 1
                                                processed_files.add(documento_file)
                                    else:
                                        print(f"No file found for document: {doc['tipoDocumento']}")
                            else:
                                print('No hay documentos')
                        except Exception as e:
                            error_message = str(e)
                            log_error(error_message, request.user.username)

                    except Exception as e:
                        error_message = str(e)
                        log_error(error_message, request.user.username)
                    
                   

                    return redirect('cotizacion_detail', pk=int(form.instance.NumeroCotizacion))
                    #return render(request, 'fideicomiso_form.html', {'form': form, 'resultado': resultado})

                except Exception as e:
                    logger.error("Error saving form: %s", e)
                    messages.error(request, 'An error occurred while saving the form.')
            
                #--------
                
               
                
                return render(request, 'fideicomiso_form.html', {'form': form, 'resultado': resultado})

                    
            
              
            except Exception as e:
                logger.error("Error in fideicomiso_view: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
                print(e)
                
        else:
            print(form.errors)
    else:
        form = FideicomisoForm(instance = cotizacion)
    
        if not cotizacion:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.sucursal is not None:
                form.fields['sucursal'].initial = user_profile.sucursal

            if user_profile.oficial is not None:
                form.fields['oficial'].initial = user_profile.oficial

    context = {
        'form': form,
        'resultado': resultado,
        'cotizacion': cotizacion,
    }


    return render(request, 'fideicomiso_form.html', context)

