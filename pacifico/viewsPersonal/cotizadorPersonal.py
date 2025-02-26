
import logging
from ..models import CotizacionDocumento, UserProfile

def log_error(message, username):
    logger.error(f"User: {username}, Error: {message}")
from decimal import Decimal
import datetime
from django.shortcuts import render, redirect
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .personalForms import PrestamoPersonalForm
from ..prestamoPersonal.calculoPP import generarPP




logger = logging.getLogger(__name__)


@login_required
def cotizacionPrestamoPersonal(request):
    resultado = None
    if request.method == 'POST':
        form = PrestamoPersonalForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                
                # Extract form data
                edad = form.cleaned_data['edad']
                sexo = form.cleaned_data['sexo']
                jubilado = form.cleaned_data['jubilado']
                nombreCliente = form.cleaned_data['nombreCliente']
                cotMontoPrestamo = Decimal(form.cleaned_data['montoPrestamo'])
                calcTasaInteres = 10 / 100
                
                calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
               
                auxPlazoPago = form.cleaned_data['plazoPago']
                patrono = form.cleaned_data['patronoCodigo']
                fecha_inicioPago = form.cleaned_data['fechaInicioPago']
                porServDesc = form.cleaned_data['porServDesc']
                selectDescuento = form.cleaned_data['selectDescuento']
                periodoPago = form.cleaned_data['periodoPago']

               
                #if patrono is None: patrono = 9999
                if patrono is None: patrono = 9999

                sucursal = 13
                auxPeriocidad = int(periodoPago)
               
                forma_pago = 4 #verificar
                #COLECTIVO DE CREDITO
                aseguradora = form.cleaned_data['aseguradora']
                #print('aseguradora', aseguradora)
                codigoSeguro = aseguradora.codigo
                r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
                comisionVendedor = form.cleaned_data['vendedorComision']
                cantPagosSeguro = form.cleaned_data['cantPagosSeguro']
                sucursal = form.cleaned_data['sucursal']
               

               
                #parse cotMontoPRestamo to float
                cotMontoPrestamo = float(cotMontoPrestamo)
                calcTasaInteres = float(calcTasaInteres)
                calcComiCierre = float(calcComiCierre)
                r_deseada = float(r_deseada)
                comisionVendedor = float(comisionVendedor)
                
                sucursal = int(sucursal)
                
                params = {
                    'tipoPrestamo': 'PERSONAL',
                    'edad': edad,
                    'sucursal': sucursal,
                    'sexo': sexo,
                    'jubilado': jubilado,
                    'cotMontoPrestamo': cotMontoPrestamo,
                    'fecha_inicioPago': fecha_inicioPago,
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
                    'porServDesc': porServDesc,
                    'selectDescuento': selectDescuento,  
                }

              
               
                resultado = generarPP(params)
                print("--------finalizado---------")
                resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra']/2,2) * 2
                # print in ta table format reusltado

                #resultado = calculoInicial(resultado,form, sexo, montoMensualSeguro, montoanualSeguro, auxPlazoPago, montoLetraSeguroAdelantado, aseguradora)


               

                
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
              
                form.instance.patrono = resultado['nombreEmpresa']
                form.instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                
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
            
 
                
                return render(request, 'prestamoPersonal.html', {'form': form, 'resultado': resultado})

                    
            
              
            except Exception as e:
                logger.error("Error in prest personal: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
                print(e)
                
        else:
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
    else:
        form = PrestamoPersonalForm()
    
    #check user sucursal, is not none set form.sucursal to user.sucursal
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.sucursal is not None:
            form.fields['sucursal'].initial = user_profile.sucursal
        
        if user_profile.oficial is not None:
            form.fields['oficial'].initial = user_profile.oficial

    
    
    context = {
        'form': form,
        'resultado': resultado,
    }

    if user_profile.pruebaFuncionalidades:
        context['pruebaFuncionalidades'] = True

    return render(request, 'prestamoPersonal.html', context)
