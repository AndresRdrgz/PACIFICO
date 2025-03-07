
import logging
from ..models import CotizacionDocumento, UserProfile, Cotizacion
from django.shortcuts import get_object_or_404

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
import pprint
from ..viewsFideicomiso.cotizadorFideicomiso import perform_fideicomiso_calculation, prepResultado, aplicaCodeudor, set_calculated_values, convert_decimal_to_float, set_calculated_values2, calculoInicial






logger = logging.getLogger(__name__)
def cotizacionDetail_pp(request, pk):
    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=pk)
    original_numero = cotizacion.NumeroCotizacion  # Store original number
   
    form = PrestamoPersonalForm(instance=cotizacion)
    consulta = {
        'consulta': True,
    }

    resultado = prepResultado(cotizacion)
    context = {
        'form': form,
        'cotizacion': cotizacion,
        'resultado': resultado,
        'consulta': consulta,
    }

    documentos = CotizacionDocumento.objects.filter(cotizacion=cotizacion)
    context['documentos'] = documentos

    if request.user.userprofile.pruebaFuncionalidades:
        context['pruebaFuncionalidades'] = True

    if request.method == 'POST':
        form = PrestamoPersonalForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            try:
                aseguradora = form.cleaned_data['aseguradora']
                form_data = form.cleaned_data
                resultado = perform_fideicomiso_calculation(form)

                # Create a new form instance to save a new record
                new_form = PrestamoPersonalForm(request.POST)
                #guardar resultado en nueva intancia
                #save resultado['tasaEstimada'] in form instance
                #print("Guardando resultado en nueva instancia")
                pp = pprint.PrettyPrinter(indent=4)
                #pp.pprint(resultado)
                #resultado['wrkLetraSinSeguros'] = resultado['wrkMontoLetra']  - resultado['wrkLetraSeguro']
                #resultado['wrkLetraSinSeguros'] = round(resultado['wrkLetraSinSeguros'], 2)
                if form.cleaned_data['aplicaCodeudor'] == "si":
                    print('aplica codeudor - CALCULAR NIVEL DE ENDEUDAMIENTO')
                    codeudorResultado = {
                        'primaMonto': form.cleaned_data['coprimaMonto'],
                        'bonosMonto': form.cleaned_data['cobonosMonto'],
                        'otrosMonto': form.cleaned_data['cootrosMonto'],
                        'horasExtrasMonto': form.cleaned_data['cohorasExtrasMonto'],
                        'siacapMonto': form.cleaned_data['cosiacapMonto'],
                        'praaMonto': form.cleaned_data['copraaMonto'],
                        'dirOtrosMonto1': form.cleaned_data['codirOtrosMonto1'],
                        'dirOtrosMonto2': form.cleaned_data['codirOtrosMonto2'],
                        'dirOtrosMonto3': form.cleaned_data['codirOtrosMonto3'],
                        'dirOtrosMonto4': form.cleaned_data['codirOtrosMonto4'],
                        'pagoVoluntarioMonto1' : form.cleaned_data['copagoVoluntarioMonto1'],
                        'pagoVoluntarioMonto2' : form.cleaned_data['copagoVoluntarioMonto2'],
                        'pagoVoluntarioMonto3' : form.cleaned_data['copagoVoluntarioMonto3'],
                        'pagoVoluntarioMonto4' : form.cleaned_data['copagoVoluntarioMonto4'],
                        'pagoVoluntarioMonto5' : form.cleaned_data['copagoVoluntarioMonto5'],
                        'pagoVoluntarioMonto6' : form.cleaned_data['copagoVoluntarioMonto6'],
                        'salarioBaseMensual' : form.cleaned_data['codeudorIngresos'],
                        'cartera' : form.cleaned_data['codeudorCartera'],
                        'wrkLetraConSeguros' : resultado['wrkLetraConSeguros'],

                    }
                    
                    codeudorResultado = convert_decimal_to_float(codeudorResultado)
                    print('iniciar nivel codeudor')
                    resultadoNivelCodeudor = nivelEndeudamiento(codeudorResultado)
                    print('resultadoNivelCodeudor', resultadoNivelCodeudor)
                    new_form.instance.cosalarioBaseMensual = codeudorResultado['salarioBaseMensual']
                    new_form.instance.cototalDescuentosLegales = resultadoNivelCodeudor['totalDescuentosLegales']
                    new_form.instance.cototalDescuentoDirecto = resultadoNivelCodeudor['totalDescuentoDirecto']
                    new_form.instance.cototalPagoVoluntario = resultadoNivelCodeudor['totalPagoVoluntario']
                    new_form.instance.cosalarioNetoActual = resultadoNivelCodeudor['salarioNetoActual']
                    new_form.instance.cosalarioNeto = resultadoNivelCodeudor['salarioNeto']
                    new_form.instance.coporSalarioNeto = resultadoNivelCodeudor['porSalarioNeto']
                    new_form.instance.cototalIngresosAdicionales = resultadoNivelCodeudor['totalIngresosAdicionales']
                    new_form.instance.cototalIngresosMensualesCompleto = resultadoNivelCodeudor['totalIngresosMensualesCompleto']
                    new_form.instance.cototalDescuentosLegalesCompleto = resultadoNivelCodeudor['totalDescuentosLegalesCompleto']
                    new_form.instance.cosalarioNetoActualCompleto = resultadoNivelCodeudor['salarioNetoActualCompleto']
                    new_form.instance.cosalarioNetoCompleto = resultadoNivelCodeudor['salarioNetoCompleto']
                    new_form.instance.coporSalarioNetoCompleto = resultadoNivelCodeudor['porSalarioNetoCompleto']

                #---------
                new_form.instance.tasaEstimada = resultado['tasaEstimada']
                new_form.instance.tasaBruta = resultado['tasaBruta']
                new_form.instance.r1 = resultado['r1']
                new_form.instance.auxMonto2 = resultado['auxMonto2']
                new_form.instance.wrkMontoLetra = resultado['wrkMontoLetra']
                new_form.instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
                new_form.instance.wrkLetraSinSeguros = resultado['wrkLetraSinSeguros']
                new_form.instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
                new_form.instance.calcMontoNotaria = resultado['calcMontoNotaria']
                new_form.instance.calcMontoTimbres = resultado['calcMontoTimbres']
                new_form.instance.tablaTotalPagos = resultado['tablaTotalPagos']
                new_form.instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
                new_form.instance.tablaTotalFeci = resultado['tablaTotalFeci']
                new_form.instance.tablaTotalInteres = resultado['tablaTotalInteres']
                new_form.instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
                new_form.instance.manejo_5porc = resultado['manejo_5porc']
                new_form.instance.valorAuto = resultado['valorAuto']
                new_form.instance.aseguradora = aseguradora
                new_form.instance.siacapMonto = resultado['siacapMonto']
                new_form.instance.siacapDcto = resultado['siacapDcto']
                new_form.instance.praaMonto = resultado['praaMonto']
                new_form.instance.praaDcto = resultado['praaDcto']
                #resultado nivel de endeuamiento - real
                new_form.instance.salarioBaseMensual = resultado['salarioBaseMensual']
                new_form.instance.totalDescuentosLegales = resultado['totalDescuentosLegales']
                new_form.instance.totalDescuentoDirecto = resultado['totalDescuentoDirecto']
                new_form.instance.totalPagoVoluntario = resultado['totalPagoVoluntario']
                new_form.instance.salarioNetoActual = resultado['salarioNetoActual']
                new_form.instance.salarioNeto = resultado['salarioNeto']
                new_form.instance.porSalarioNeto = resultado['porSalarioNeto']
                new_form.instance.totalIngresosAdicionales = resultado['totalIngresosAdicionales']
                new_form.instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
                new_form.instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
                new_form.instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
                new_form.instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
                new_form.instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']
                # ------------------- Save the new record -------------------
                if new_form.is_valid():
                    new_instance = new_form.save(commit=False)
                    new_instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                     # Set the calculated values on the new instance
                    new_instance.wrkMontoLetra = resultado['wrkMontoLetra']
                    
                    new_instance.montoManejoT = resultado['montoManejoT']
                    new_instance.monto_manejo_b = resultado['montoManejoB']
                    new_instance.tasaEstimada = resultado['tasaEstimada']
                    new_instance.r1 = resultado['r1']
                    new_instance.auxMonto2 = resultado['auxMonto2']
                    new_instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
                    new_instance.calcMontoNotaria = resultado['calcMontoNotaria']
                    new_instance.calcMontoTimbres = resultado['calcMontoTimbres']
                    new_instance.tablaTotalPagos = resultado['tablaTotalPagos']
                    new_instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
                    new_instance.tablaTotalFeci = resultado['tablaTotalFeci']
                    new_instance.tablaTotalInteres = resultado['tablaTotalInteres']
                    new_instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
                    new_instance.manejo_5porc = resultado['manejo_5porc']
                    new_instance.valorAuto = resultado['valorAuto']
                    new_instance.aseguradora = aseguradora
                    new_instance.siacapMonto = resultado['siacapMonto']
                    new_instance.siacapDcto = resultado['siacapDcto']
                    new_instance.praaMonto = resultado['praaMonto']
                    new_instance.praaDcto = resultado['praaDcto']
                    new_instance.wrkLetraSinSeguros = resultado['wrkLetraSinSeguros']
                    new_instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
                    new_instance.tasaBruta = resultado['tasaBruta']
                    #resultado nivel de endeuamiento - real
                    new_instance.salarioBaseMensual = resultado['salarioBaseMensual']
                    new_instance.totalDescuentosLegales = resultado['totalDescuentosLegales']
                    new_instance.totalDescuentoDirecto = resultado['totalDescuentoDirecto']
                    new_instance.totalPagoVoluntario = resultado['totalPagoVoluntario']
                    new_instance.salarioNetoActual = resultado['salarioNetoActual']
                    new_instance.salarioNeto = resultado['salarioNeto']
                    new_instance.porSalarioNeto = resultado['porSalarioNeto']
                    new_instance.totalIngresosAdicionales = resultado['totalIngresosAdicionales']
                    new_instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
                    new_instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
                    new_instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
                    new_instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
                    new_instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']
                    #resultado codeudor nivel de endeudamiento
                    if form.cleaned_data['aplicaCodeudor'] == "si":
                        new_instance.cosalarioBaseMensual = codeudorResultado['salarioBaseMensual']
                        new_instance.cototalDescuentosLegales = resultadoNivelCodeudor['totalDescuentosLegales']
                        new_instance.cototalDescuentoDirecto = resultadoNivelCodeudor['totalDescuentoDirecto']
                        new_instance.cototalPagoVoluntario = resultadoNivelCodeudor['totalPagoVoluntario']
                        new_instance.cosalarioNetoActual = resultadoNivelCodeudor['salarioNetoActual']
                        new_instance.cosalarioNeto = resultadoNivelCodeudor['salarioNeto']
                        new_instance.coporSalarioNeto = resultadoNivelCodeudor['porSalarioNeto']
                        new_instance.cototalIngresosAdicionales = resultadoNivelCodeudor['totalIngresosAdicionales']
                        new_instance.cototalIngresosMensualesCompleto = resultadoNivelCodeudor['totalIngresosMensualesCompleto']
                        new_instance.cototalDescuentosLegalesCompleto = resultadoNivelCodeudor['totalDescuentosLegalesCompleto']
                        new_instance.cosalarioNetoActualCompleto = resultadoNivelCodeudor['salarioNetoActualCompleto']
                        new_instance.cosalarioNetoCompleto = resultadoNivelCodeudor['salarioNetoCompleto']
                        new_instance.coporSalarioNetoCompleto = resultadoNivelCodeudor['porSalarioNetoCompleto']
                    #-------                                                                                                                        

                    new_instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                    #------- SAFE SAVE ------------
                    for field in new_instance._meta.fields:
                        print(field.name, field.value_from_object(new_instance))
                    print("intentando guardar")
                    new_instance.save()
                    print("se guardo -",new_form.instance.NumeroCotizacion)
                     # Get the NumeroCotizacion after saving the form
                    numero_cotizacion = int(new_form.instance.NumeroCotizacion)
                    resultado['numero_cotizacion'] = numero_cotizacion
                    print('numero_cotizacion -',numero_cotizacion)
                    request.session['resultado'] = resultado
                    print("resultados guardados")
                    return redirect('cotizacion_detail', pk=int(new_form.instance.NumeroCotizacion))
                    
                else:
                    logger.warning("New form is not valid: %s", new_form.errors)
                    messages.error(request, 'An error occurred while creating a new record.')
                    error_message = str(e)
                    log_error(error_message, request.user.username)
               
            except Exception as e:
                print('Error:', e)
                error_message = str(e)
                log_error(error_message, request.user.username)
                pass
                
        else:
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
            
            
    return render(request, 'prestamoPersonal.html', context)



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
                if form.cleaned_data['tasaInteres'] is not None:
                    calcTasaInteres = Decimal(form.cleaned_data['tasaInteres']) / 100
                print("tasa interes",calcTasaInteres)
               
                calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
                auxPlazoPago = form.cleaned_data['plazoPago']
                patrono = form.cleaned_data['patronoCodigo']
                fecha_inicioPago = form.cleaned_data['fechaInicioPago']
                porServDesc = form.cleaned_data['porServDesc']
                selectDescuento = form.cleaned_data['selectDescuento']
                periodoPago = form.cleaned_data['periodoPago']

                if patrono is None: patrono = 9999

                sucursal = 13
                auxPeriocidad = int(periodoPago)
                forma_pago = 4  # verificar
                aseguradora = form.cleaned_data['aseguradora']
                codigoSeguro = aseguradora.codigo
                r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
                comisionVendedor = form.cleaned_data['vendedorComision']
                cantPagosSeguro = form.cleaned_data['cantPagosSeguro']
                sucursal = form.cleaned_data['sucursal']

                cotMontoPrestamo = float(cotMontoPrestamo)
                calcTasaInteres = float(calcTasaInteres)
                calcComiCierre = float(calcComiCierre)
                r_deseada = float(r_deseada)
                comisionVendedor = float(comisionVendedor)
                sucursal = int(sucursal)
                pagaDiciembre = form.cleaned_data['pagaDiciembre']

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
                    'pagaDiciembre': pagaDiciembre,
                }
                print("params",params)
                
                resultado, iteration_data = generarPP(params)
                print("--------finalizado---------")
                resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra'] / 2, 2) * 2

                # Convert datetime.date objects to strings
                for key, value in resultado.items():
                    if isinstance(value, datetime.date):
                        resultado[key] = value.strftime('%Y-%m-%d')

                form.instance.tasaEstimada = resultado['tasaEstimada']
                form.instance.tasaBruta = resultado['tasaBruta']
                form.instance.r1 = resultado['r1']
                form.instance.montoPrestamo = resultado['cotMontoPrestamo']
                form.instance.auxMonto2 = round(Decimal(resultado['auxMonto2']), 2)
                form.instance.montoManejoT = resultado['montoManejoT']
                form.instance.monto_manejo_b = resultado['montoManejoB']
                form.instance.wrkMontoLetra = resultado['wrkMontoLetra']
                form.instance.wrkLetraSeguro = resultado['wrkLetraSeguro']
                form.instance.calcComiCierreFinal = resultado['calcComiCierreFinal']
                form.instance.calcMontoNotaria = resultado['calcMontoNotaria']
                form.instance.calcMontoTimbres = resultado['calcMontoTimbres']
                form.instance.tablaTotalPagos = resultado['tablaTotalPagos']
                form.instance.tablaTotalSeguro = resultado['tablaTotalSeguro']
                form.instance.tablaTotalFeci = resultado['tablaTotalFeci']
                form.instance.tablaTotalInteres = resultado['tablaTotalInteres']
                form.instance.tablaTotalMontoCapital = resultado['tablaTotalMontoCapital']
                form.instance.manejo_5porc = resultado['manejo_5porc']
                form.instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                form.instance.tipoPrestamo = 'personal'

                try:
                    for field in form.instance._meta.fields:
                        #print(field.name, field.value_from_object(form.instance))
                        pass

                    print("intentando guardar")
                    try:
                        form.save()
                        print("guardado")
                        numero_cotizacion = form.instance.NumeroCotizacion
                        resultado['numero_cotizacion'] = int(numero_cotizacion)
                        # Convert Decimal objects to float
                        for key, value in resultado.items():
                            if isinstance(value, Decimal):
                                resultado[key] = float(value)
                        request.session['resultado'] = resultado
                        print("redirecting,",numero_cotizacion)
                    except Exception as e:
                        error_message = str(e)
                        log_error(error_message, request.user.username)

                    print("mmmmmmm")
                    #return redirect('cotizacionDetail_pp', numero_cotizacion)
                    return render(request, 'prestamoPersonal.html', {'form': form, 'resultado': resultado, 'iteration_data': iteration_data})

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