from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import FideicomisoForm, ClienteForm, AseguradoraForm
from .fideicomiso.fideicomiso import generarFideicomiso2, generarFideicomiso3, generarFideicomiso4
from .analisisConsulta.nivelEndeudamiento import nivelEndeudamiento  # Corrected import statement
import datetime
import decimal
import logging
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from openpyxl import load_workbook
import os
from django.conf import settings
from django.http import JsonResponse
import json
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from .fideicomiso.sura import cotizacionSeguroAuto
from .models import Cotizacion, Cliente, Aseguradora
import openpyxl
import pprint
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .viewsFideicomiso.cotizadorFideicomiso import perform_fideicomiso_calculation
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User



# Get an instance of a logger
logger = logging.getLogger(__name__)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'

@user_passes_test(lambda u: u.is_superuser)
def view_active_sessions(request):
    # Get all non-expired sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_sessions = []
    
    # Get user details from each session
    for session in sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id:
            user = User.objects.get(id=user_id)
            user_sessions.append({
                'username': user.username,
                'session_key': session.session_key,
                'expire_date': session.expire_date,
                'email': user.email
            })
    
    return render(request, 'active_sessions.html', {'sessions': user_sessions})

@user_passes_test(lambda u: u.is_superuser)
def terminate_all_sessions(request):
    sessions = Session.objects.all()
    for session in sessions:
        session.delete()
    messages.success(request, 'All sessions have been terminated and users have been logged out.')
    return redirect('active_sessions')

def aseguradora_create(request):
    if request.method == 'POST':
        form = AseguradoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('aseguradora_list')
    else:
        form = AseguradoraForm()
    return render(request, 'aseguradora_form.html', {'form': form})

def aseguradora_list(request):
    aseguradoras = Aseguradora.objects.all()
    return render(request, 'aseguradora_list.html', {'aseguradoras': aseguradoras})

@login_required
def cotizacionDetail(request, pk):
    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=pk)
    form = FideicomisoForm(instance=cotizacion)
    consulta = {
        'consulta': True,
    }
    resultado = {
        'auxMonto2': cotizacion.auxMonto2,
        'r1': cotizacion.r1,
        'tasaEstimada': cotizacion.tasaEstimada,
        'calcComiCierreFinal': cotizacion.calcComiCierreFinal,
        'auxPlazoPago': cotizacion.plazoPago,
        'wrkLetraSinSeguros': cotizacion.wrkLetraSinSeguros,
        'wrkLetraSeguro': cotizacion.wrkLetraSeguro,
        'wrkMontoLetra': cotizacion.wrkMontoLetra,
        'montoMensualSeguro': cotizacion.montoMensualSeguro,
        'wrkLetraConSeguros': cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro,
        'tablaTotalPagos': cotizacion.tablaTotalPagos,
        'nombreCliente': cotizacion.nombreCliente,
        'valorAuto': cotizacion.valorAuto,
        'abono': cotizacion.abono,
        'salarioBaseMensual': cotizacion.salarioBaseMensual,
        'totalDescuentosLegales': cotizacion.totalDescuentosLegales,
        'totalDescuentoDirecto': cotizacion.totalDescuentoDirecto,
        'totalPagoVoluntario': cotizacion.totalPagoVoluntario,
        'salarioNetoActual': cotizacion.salarioNetoActual,
        'salarioNeto': cotizacion.salarioNeto,
        'porSalarioNeto': cotizacion.porSalarioNeto,
        'totalIngresosAdicionales': cotizacion.totalIngresosAdicionales,
        'totalIngresosMensualesCompleto': cotizacion.totalIngresosMensualesCompleto,
        'totalDescuentosLegalesCompleto': cotizacion.totalDescuentosLegalesCompleto,
        'salarioNetoActualCompleto': cotizacion.salarioNetoActualCompleto,
        'salarioNetoCompleto': cotizacion.salarioNetoCompleto,
        'porSalarioNetoCompleto': cotizacion.porSalarioNetoCompleto,
        'numero_cotizacion': cotizacion.NumeroCotizacion

 }

    print('resultado', resultado)
    context = {
        'form': form,
        'cotizacion': cotizacion,
        'resultado': resultado,
        'consulta': consulta,
    }

    if request.method == 'POST':
        form = FideicomisoForm(request.POST, instance=cotizacion)
        if form.is_valid():
            try:
                aseguradora = form.cleaned_data['aseguradora']
                form_data = form.cleaned_data
                resultado = perform_fideicomiso_calculation(form)

                # Create a new form instance to save a new record
                new_form = FideicomisoForm(request.POST)
                #guardar resultado en nueva intancia
                #save resultado['tasaEstimada'] in form instance
                print("Guardando resultado en nueva instancia")
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(resultado)
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

                    new_instance.save()
                    messages.success(request, 'New record has been created successfully.')
                     # Get the NumeroCotizacion after saving the form
                    numero_cotizacion = new_form.instance.NumeroCotizacion
                    resultado['numero_cotizacion'] = int(numero_cotizacion)
                    #if resultado numero_cotizacion is not a number set it to = 0
                    if not isinstance(resultado['numero_cotizacion'], int):
                        resultado['numero_cotizacion'] = 0
                    logger.info('NumeroCotizacion: %s', numero_cotizacion)
                    request.session['resultado'] = resultado


                    
                    return redirect('cotizacion_detail', pk=int(form.instance.NumeroCotizacion))
                    
                else:
                    logger.warning("New form is not valid: %s", new_form.errors)
                    messages.error(request, 'An error occurred while creating a new record.')
               
            except Exception as e:
                print('Error:', e)
                pass
                
        else:
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
            
            
    return render(request, 'fideicomiso_form.html', context)



@login_required
def cotizacion_detail(request, pk):
    print('ID cotizacion', pk)  
    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=pk)
    print('cotizacion', cotizacion)
    form = FideicomisoForm(instance=cotizacion)
    consulta = {
        'consulta': True,
    }
    resultado = {
        'auxMonto2': cotizacion.auxMonto2,
        'r1': cotizacion.r1,
        'tasaEstimada': cotizacion.tasaEstimada,
        'calcComiCierreFinal': cotizacion.calcComiCierreFinal,
        'auxPlazoPago': cotizacion.plazoPago,
        'wrkLetraSinSeguros': cotizacion.wrkLetraSinSeguros,
        'wrkLetraSeguro': cotizacion.wrkLetraSeguro,
        'wrkMontoLetra': cotizacion.wrkMontoLetra,
        'montoMensualSeguro': cotizacion.montoMensualSeguro,
        'wrkLetraConSeguros': cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro,
        'tablaTotalPagos': cotizacion.tablaTotalPagos,
        'nombreCliente': cotizacion.nombreCliente,
        'valorAuto': cotizacion.valorAuto,
        'abono': cotizacion.abono,
        'salarioBaseMensual': cotizacion.salarioBaseMensual,
        'totalDescuentosLegales': cotizacion.totalDescuentosLegales,
        'totalDescuentoDirecto': cotizacion.totalDescuentoDirecto,
        'totalPagoVoluntario': cotizacion.totalPagoVoluntario,
        'salarioNetoActual': cotizacion.salarioNetoActual,
        'salarioNeto': cotizacion.salarioNeto,
        'porSalarioNeto': cotizacion.porSalarioNeto,
        'totalIngresosAdicionales': cotizacion.totalIngresosAdicionales,
        'totalIngresosMensualesCompleto': cotizacion.totalIngresosMensualesCompleto,
        'totalDescuentosLegalesCompleto': cotizacion.totalDescuentosLegalesCompleto,
        'salarioNetoActualCompleto': cotizacion.salarioNetoActualCompleto,
        'salarioNetoCompleto': cotizacion.salarioNetoCompleto,
        'porSalarioNetoCompleto': cotizacion.porSalarioNetoCompleto

 }

    print('resultado', resultado)
    context = {
        'form': form,
        'cotizacion': cotizacion,
        'resultado': resultado,
        'consulta': consulta,
    }
    return render(request, 'fideicomiso_form.html', context)

@login_required
def cliente_profile(request, cedula):
    cliente = get_object_or_404(Cliente, cedulaCliente=cedula)
    cotizaciones = Cotizacion.objects.filter(cedulaCliente=cedula)

    if request.user.is_authenticated:
        cotizaciones = cotizaciones.filter(added_by=request.user
        )

    #If user is staff show all cotizaciones
    if request.user.is_staff:
        cotizaciones = Cotizacion.objects.filter(cedulaCliente=cedula)
    

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('cliente_profile', cedula=cliente.cedula)
    else:
        form = ClienteForm(instance=cliente)

    context = {
        'cliente': cliente,
        'cotizaciones': cotizaciones,
        'form': form,
    }
    return render(request, 'cliente_profile.html', context)

@login_required
def clientesList(request):
    clientes = Cliente.objects.all()

    #sort by newest first
    
    return render(request, 'clientesList.html', {'clientes': clientes})


@login_required
def download_cotizaciones_excel(request):
    cotizaciones = Cotizacion.objects.all()

    cotizaciones = cotizaciones.order_by('-created_at')

    # Create an in-memory workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Cotizaciones"
    
    # Define the headers
    headers = [
        "ID", "Oficial", "Sucursal", "Nombre Cliente", "Cédula Cliente", "Fecha Nacimiento", "Edad", "Sexo", 
        "Jubilado", "Patrono", "Patrono Código", "Vendedor", "Vendedor Comisión", "Aseguradora", "Tasa Bruta", 
        "Marca", "Modelo", "Fecha Inicio Pago", "Monto Préstamo", "Tasa Interés", "Comisión Cierre", 
        "Comisión Cierre Final", "Plazo Pago", "R Deseada", "Tasa Estimada", "R1", "Monto 2", "Monto Letra", 
        "Monto Notaría", "Monto Timbres", "Manejo 5%", "Total Pagos", "Total Seguro", "Total Feci", 
        "Total Interés", "Total Monto Capital"
    ]
    
    # Write the header row
    sheet.append(headers)

    # Write the data rows
    for cotizacion in cotizaciones:
        row = [
            cotizacion.id,
            cotizacion.oficial,
            cotizacion.sucursal,
            cotizacion.nombreCliente,
            cotizacion.cedulaCliente,
            cotizacion.fechaNacimiento,
            cotizacion.edad,
            cotizacion.sexo,
            cotizacion.jubilado,
            cotizacion.patrono,
            cotizacion.patronoCodigo,
            cotizacion.vendedor,
            cotizacion.vendedorComision,
            str(cotizacion.aseguradora),  # Convert aseguradora to string
            cotizacion.tasaBruta,
            cotizacion.marca,
            cotizacion.modelo,
            cotizacion.fechaInicioPago,
            cotizacion.montoPrestamo,
            cotizacion.tasaInteres,
            cotizacion.comiCierre,
            cotizacion.calcComiCierreFinal,
            cotizacion.plazoPago,
            cotizacion.r_deseada,
            cotizacion.tasaEstimada,
            cotizacion.r1,
            cotizacion.auxMonto2,
            cotizacion.wrkMontoLetra,
            cotizacion.calcMontoNotaria,
            cotizacion.calcMontoTimbres,
            cotizacion.manejo_5porc,
            cotizacion.tablaTotalPagos,
            cotizacion.tablaTotalSeguro,
            cotizacion.tablaTotalFeci,
            cotizacion.tablaTotalInteres,
            cotizacion.tablaTotalMontoCapital,
        ]
        sheet.append(row)

    # Set the response content type to Excel
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="cotizaciones.xlsx"'

    # Save the workbook to the response
    workbook.save(response)

    return response

@login_required
def cotizacionesList(request):
    cotizaciones = Cotizacion.objects.all()

    #sort by newest first
    cotizaciones = cotizaciones.order_by('-created_at')

    #Filter cotizaciones by addedBy current user
    if request.user.is_authenticated:
        cotizaciones = cotizaciones.filter(added_by=request.user
        )

    #If user is staff show all cotizaciones
    if request.user.is_staff:
        cotizaciones = Cotizacion.objects.all()
    
    return render(request, 'cotizacionesList.html', {'cotizaciones': cotizaciones})



@csrf_exempt
def cotizacion_seguro_auto(request):
    if request.method == 'POST':
        #print all the data received
        print('request.POST', request.POST)
        marca = request.POST.get('marca')
        
        modelo = request.POST.get('modelo')
        
        year_auto = int(request.POST.get('year_auto'))
        
        valor = float(request.POST.get('valor'))
        years_financiamiento = int(request.POST.get('years_financiamiento'))

     


        # Call the cotizacionSeguroAuto function
        result = cotizacionSeguroAuto(marca, modelo, year_auto, valor, years_financiamiento)
        print('result', result)
        # Return the result as JSON
        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def convert_decimal_to_float(data):
    print('data', data)
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
            print('key', key)
    return data



def get_lineas(request):
    try:
        marca = request.GET.get('marca')
        BASE_DIR = Path(__file__).resolve().parent.parent
        with open(BASE_DIR / 'static/insumos/autos.json') as f:
            choices_data = json.load(f)
        lineas = [item['LINEA'] for item in choices_data if item['MARCA'] == marca]
        return JsonResponse({'lineas': lineas})
    except Exception as e:
        logger.error("Error in get_lineas: %s", e)
        return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)

@login_required
def generate_report(request, numero_cotizacion):
    # Retrieve the cotizacion record based on numero_cotizacion
    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=numero_cotizacion)
    
    # Populate resultado with the values from the cotizacion record
    resultado = {
        'oficial': cotizacion.oficial,
        'nombreCliente': cotizacion.nombreCliente,
        'cedulaCliente': cotizacion.cedulaCliente,
        'tipoDocumento': cotizacion.tipoDocumento,
        'edad': cotizacion.edad,
        'sexo': cotizacion.sexo,
        'apcScore': cotizacion.apcScore,
        'apcPI': cotizacion.apcPI,
        'cotPlazoPago': cotizacion.plazoPago,
        'r1': cotizacion.r1,
        'abonoPorcentaje': cotizacion.abonoPorcentaje,
        'abono': cotizacion.abono,
        'cashback': cotizacion.cashback,
        'valorAuto': cotizacion.valorAuto,
        'calcMontoTimbres': cotizacion.calcMontoTimbres,
        'tasaBruta': cotizacion.tasaBruta,
        'cotMontoPrestamo': cotizacion.montoPrestamo,
        'calcMontoNotaria': cotizacion.calcMontoNotaria,
        'promoPublicidad': 50,
        'montoLetraSeguroAdelantado': cotizacion.mesesFinanciaSeguro * cotizacion.montoMensualSeguro,
        'calcComiCierreFinal': cotizacion.calcComiCierreFinal,
        'manejo_5porc': cotizacion.manejo_5porc,
        'auxMonto2': cotizacion.auxMonto2,
        'wrkLetraSinSeguros': cotizacion.wrkLetraSinSeguros,
        'wrkLetraSeguro': cotizacion.wrkLetraSeguro,
        'wrkMontoLetra': cotizacion.wrkMontoLetra,
        'montoMensualSeguro': cotizacion.montoMensualSeguro,
        'wrkLetraConSeguros': cotizacion.wrkMontoLetra + cotizacion.montoMensualSeguro,
        'tablaTotalPagos': cotizacion.tablaTotalPagos,
        'vendedor': cotizacion.vendedor,
        'comisionVendedor': cotizacion.vendedorComision,
        'marcaAuto': cotizacion.marca,
        'lineaAuto': cotizacion.modelo,
        'yearAuto': cotizacion.yearCarro,
        'transmision': cotizacion.transmisionAuto,
        'nuevoAuto': cotizacion.nuevoAuto,
        'kilometrajeAuto': cotizacion.kilometrajeAuto,
        'observaciones': cotizacion.observaciones,
        'salarioBaseMensual': cotizacion.salarioBaseMensual,
        'tiempoServicio': cotizacion.tiempoServicio,
        'ingresos': cotizacion.ingresos,
        'nombreEmpresa': cotizacion.nombreEmpresa,
        'referenciasAPC': cotizacion.referenciasAPC,
        'cartera': cotizacion.cartera,
        'licencia': cotizacion.licencia,
        'posicion': cotizacion.posicion,
        'perfilUniversitario': cotizacion.perfilUniversitario,
        'horasExtrasMonto': cotizacion.horasExtrasMonto,
        'otrosMonto': cotizacion.otrosMonto,
        'montoanualSeguro': cotizacion.montoanualSeguro,
        'otrosDcto': cotizacion.otrosDcto,
        'bonosMonto': cotizacion.bonosMonto,
        'bonosDcto': cotizacion.bonosDcto,
        'siacapMonto': cotizacion.siacapMonto,
        'siacapDcto': cotizacion.siacapDcto,
        'praaMonto': cotizacion.praaMonto,
        'praaDcto': cotizacion.praaDcto,
        'dirOtrosMonto1': cotizacion.dirOtrosMonto1,
        'dirOtros1': cotizacion.dirOtros1,
        'dirOtrosDcto1': cotizacion.dirOtrosDcto1,
        'dirOtrosMonto2': cotizacion.dirOtrosMonto2,
        'dirOtros2': cotizacion.dirOtros2,
        'dirOtrosDcto2': cotizacion.dirOtrosDcto2,
        'dirOtrosMonto3': cotizacion.dirOtrosMonto3,
        'dirOtros3': cotizacion.dirOtros3,
        'dirOtrosDcto3': cotizacion.dirOtrosDcto3,
        'dirOtrosMonto4': cotizacion.dirOtrosMonto4,
        'dirOtros4': cotizacion.dirOtros4,
        'dirOtrosDcto4': cotizacion.dirOtrosDcto4,
        'pagoVoluntario1': cotizacion.pagoVoluntario1,
        'pagoVoluntarioMonto1': cotizacion.pagoVoluntarioMonto1,
        'pagoVoluntarioDcto1': cotizacion.pagoVoluntarioDcto1,
        'pagoVoluntario2': cotizacion.pagoVoluntario2,
        'pagoVoluntarioMonto2': cotizacion.pagoVoluntarioMonto2,
        'pagoVoluntarioDcto2': cotizacion.pagoVoluntarioDcto2,
        'pagoVoluntario3': cotizacion.pagoVoluntario3,
        'pagoVoluntarioMonto3': cotizacion.pagoVoluntarioMonto3,
        'pagoVoluntarioDcto3': cotizacion.pagoVoluntarioDcto3,
        'pagoVoluntario4': cotizacion.pagoVoluntario4,
        'pagoVoluntarioMonto4': cotizacion.pagoVoluntarioMonto4,
        'pagoVoluntarioDcto4': cotizacion.pagoVoluntarioDcto4,
        'pagoVoluntario5': cotizacion.pagoVoluntario5,
        'pagoVoluntarioMonto5': cotizacion.pagoVoluntarioMonto5,
        'pagoVoluntarioDcto5': cotizacion.pagoVoluntarioDcto5,
        'pagoVoluntario6': cotizacion.pagoVoluntario6,
        'pagoVoluntarioMonto6': cotizacion.pagoVoluntarioMonto6,
        'pagoVoluntarioDcto6': cotizacion.pagoVoluntarioDcto6,
        'mes0': cotizacion.mes0,
        'mes1': cotizacion.mes1,
        'mes2': cotizacion.mes2,
        'mes3': cotizacion.mes3,
        'mes4': cotizacion.mes4,
        'mes5': cotizacion.mes5,
        'mes6': cotizacion.mes6,
        'mes7': cotizacion.mes7,
        'mes8': cotizacion.mes8,
        'mes9': cotizacion.mes9,
        'mes10': cotizacion.mes10,
        'mes11': cotizacion.mes11,
        'primerMes': cotizacion.primerMes,
        'tipoProrrateo': cotizacion.tipoProrrateo,
    }
    
    # Path to the static Excel file
    excel_path = os.path.join(settings.BASE_DIR, 'static/insumos', 'consultaPrestAuto.xlsx')

    if not os.path.exists(excel_path):
        return HttpResponse("File not found.", status=404)
    
    # Load the workbook and select the active sheet
    workbook = load_workbook(excel_path)
    sheet = workbook.active
    
    # Select the sheet with name "COTIZADOR PREST. AUTO"
    if "COTIZADOR PREST. AUTO" in workbook.sheetnames:
        sheet = workbook["COTIZADOR PREST. AUTO"]
    else:
        return HttpResponse("Sheet not found.", status=404)
    
    # Example: Write the resultado data to the Excel sheet
    sheet['D6'] = resultado['oficial']
    sheet['C10'] = resultado['nombreCliente']
    sheet['G10'] = resultado['cedulaCliente']
    sheet['H10'] = resultado['tipoDocumento']
    sheet['J10'] = resultado['edad']
    sheet['I10'] = resultado['sexo']
    sheet['k10'] = resultado['apcScore']
    sheet['l10'] = resultado['apcPI']
    #parametros de la cotizacion
    sheet['F14'] = resultado['cotPlazoPago']
    sheet['G14'] = resultado['r1'] / 100
    sheet['E14'] = resultado['abonoPorcentaje'] / 100
    sheet['e15'] = resultado['abono']
    print('cashback', resultado['cashback'])
    sheet['h14'] = resultado['cashback']
    sheet['C14'] = resultado['valorAuto']
    sheet['L14'] = resultado['calcMontoTimbres']
    sheet['i15'] = 'SI APLICA'
    sheet['J15'] = resultado['tasaBruta']
    if resultado['tasaBruta'] == 0:
        sheet['K15'] = 'NO'

    #sheet['H14'] = resultado['cashback']

    #DETALLES DE LA COTIZACION
    sheet['E21'] = resultado['cotMontoPrestamo']
    sheet['E23'] = resultado['calcMontoNotaria']
    sheet['E24'] = resultado['promoPublicidad']
    sheet['e26'] = resultado['montoLetraSeguroAdelantado']
    sheet['e29'] = resultado['calcComiCierreFinal'] / 100
    sheet['e30'] = resultado['manejo_5porc']
    sheet['e31'] = resultado['auxMonto2']
    sheet['E39'] = resultado['wrkLetraSinSeguros']
    sheet['E43'] = resultado['wrkLetraSinSeguros']
    sheet['e40'] = resultado['wrkLetraSeguro']
    sheet['E41'] = resultado['wrkMontoLetra']
    sheet['e42'] = resultado['montoMensualSeguro']
    sheet['E44'] = resultado['wrkLetraConSeguros']

    sheet['E46'] = resultado['tablaTotalPagos']
    
    #DATOS DEL VENDEDOR
    sheet['j18'] = resultado['vendedor']
    sheet['j20'] = resultado['comisionVendedor']

    #DATOS DEL VEHICULO
    sheet['j23'] = resultado['marcaAuto']
    sheet['j24'] = resultado['lineaAuto']
    sheet['j25'] = resultado['yearAuto']
    sheet['j30'] = resultado['montoMensualSeguro']
    sheet['j31'] = resultado['montoanualSeguro']
    sheet['j26'] = resultado['transmision']
    sheet['j27'] = resultado['nuevoAuto']
    sheet['j28'] = resultado['kilometrajeAuto']

    #motivo consulta
    sheet['H42'] = resultado['observaciones']

    #DATOS DEL DEudor
    sheet['e77'] = resultado['salarioBaseMensual']
    sheet['E49']=resultado['tiempoServicio']
    sheet['J49']=resultado['ingresos']
    sheet['E50']=resultado['nombreEmpresa'] 
    sheet['J50']=resultado['referenciasAPC']
    sheet['e51']=resultado['cartera']
    sheet['J51']=resultado['licencia']
    sheet['E52']=resultado['posicion']
    sheet['E53']=resultado['perfilUniversitario']

    if resultado['horasExtrasMonto'] is None:
        resultado['horasExtrasMonto'] = 0
    if resultado['horasExtrasMonto'] > 0:
        sheet['J78']=resultado['horasExtrasMonto']

    if resultado['otrosMonto'] is None:
        resultado['otrosMonto'] = 0
    if resultado['otrosMonto'] > 0:
        sheet['J81']=resultado['otrosMonto']
        if resultado['otrosDcto'] == True:
            sheet['K81'] = 'SÍ'
        else:
            sheet['K81'] = 'NO'

    if resultado['bonosMonto'] is None:
        resultado['bonosMonto'] = 0
    if resultado['bonosMonto'] > 0:
        sheet['J80']=resultado['bonosMonto']
        if resultado['bonosDcto'] == True:
            sheet['K80'] = 'SÍ'
        else:
            sheet['K80'] = 'NO'
        

    

    #DESCUENTO DIRECTO
    
    print('siacapMonto', resultado['siacapMonto'])
    if resultado['siacapMonto'] > 0:
        sheet['E87'] = resultado['siacapMonto']
        if resultado['siacapDcto'] == True:
            sheet['F87'] = 'SÍ'
        else:
            sheet['F87'] = 'NO'

    if resultado['praaMonto'] > 0:
        sheet['E88'] = resultado['praaMonto']
        if resultado['praaDcto'] == True:
            sheet['F88'] = 'SÍ'
        else:
            sheet['F88'] = 'NO'
    
    if resultado['dirOtrosMonto1'] is None:
        resultado['dirOtrosMonto1'] = 0
    if resultado['dirOtrosMonto1'] > 0:
        sheet['E89'] = resultado['dirOtrosMonto1']
        sheet['C89'] = resultado['dirOtros1']
        if resultado['dirOtrosDcto1'] == True:
            sheet['F89'] = 'SÍ'
        else:
            sheet['F89'] = 'NO'

    if resultado['dirOtrosMonto2'] is None:
        resultado['dirOtrosMonto2'] = 0

    if resultado['dirOtrosMonto2'] > 0:
        sheet['E90'] = resultado['dirOtrosMonto2']
        sheet['C90'] = resultado['dirOtros2']
        if resultado['dirOtrosDcto2'] == True:
            sheet['F90'] = 'SÍ'
        else:
            sheet['F90'] = 'NO'

    if resultado['dirOtrosMonto3'] is None:
        resultado['dirOtrosMonto3'] = 0

    if resultado['dirOtrosMonto3'] > 0:
        sheet['E91'] = resultado['dirOtrosMonto3']
        sheet['C91'] = resultado['dirOtros3']
        if resultado['dirOtrosDcto3'] == True:
            sheet['F91'] = 'SÍ'
        else:
            sheet['F91'] = 'NO'

    if resultado['dirOtrosMonto4'] is None:
        resultado['dirOtrosMonto4'] = 0


    if resultado['dirOtrosMonto4'] > 0:
        sheet['E92'] = resultado['dirOtrosMonto4']
        sheet['C92'] = resultado['dirOtros4']
        if resultado['dirOtrosDcto4'] == True:
            sheet['F92'] = 'SÍ'
        else:
            sheet['F92'] = 'NO'

    #pagos voluntarios
    sheet['H87'] = resultado['pagoVoluntario1']
    sheet['H88'] = resultado['pagoVoluntario2']
    sheet['H89'] = resultado['pagoVoluntario3']
    
    sheet['H90'] = resultado['pagoVoluntario4']
    
    sheet['H91'] = resultado['pagoVoluntario5']
    
    sheet['H92'] = resultado['pagoVoluntario6']
    
       

    #PARSE TRUE TO SI AND FALSE TO NO
    if resultado ['pagoVoluntarioMonto1'] is None:
        resultado['pagoVoluntarioMonto1'] = 0

    if resultado['pagoVoluntarioMonto1'] > 0:
        sheet['J87'] = resultado['pagoVoluntarioMonto1']
        if resultado['pagoVoluntarioDcto1'] == True:
            sheet['K87'] = 'SÍ'
        else:
            sheet['K87'] = 'NO'

    if resultado['pagoVoluntarioMonto2'] is None:
        resultado['pagoVoluntarioMonto2'] = 0
    if resultado['pagoVoluntarioMonto2'] > 0:
        sheet['J88'] = resultado['pagoVoluntarioMonto2']
        if resultado['pagoVoluntarioDcto2'] == True:
            sheet['K88'] = 'SÍ'
        else:
            sheet['K88'] = 'NO'

    if resultado['pagoVoluntarioMonto3'] is None:
        resultado['pagoVoluntarioMonto3'] = 0
    if resultado['pagoVoluntarioMonto3'] > 0:
        sheet['J89'] = resultado['pagoVoluntarioMonto3']
        if resultado['pagoVoluntarioDcto3'] == True:
            sheet['K89'] = 'SÍ'
        else:
            sheet['K89'] = 'NO'
    if resultado['pagoVoluntarioMonto4'] is None:
        resultado['pagoVoluntarioMonto4'] = 0

    if resultado['pagoVoluntarioMonto4'] > 0:
        sheet['J90'] = resultado['pagoVoluntarioMonto4']
        if resultado['pagoVoluntarioDcto4'] == True:
            sheet['K90'] = 'SÍ'
        else:
            sheet['K90'] = 'NO'

    if resultado['pagoVoluntarioMonto5'] is None:
        resultado['pagoVoluntarioMonto5'] = 0

    if resultado['pagoVoluntarioMonto5'] > 0:
        sheet['J91'] = resultado['pagoVoluntarioMonto5']
        if resultado['pagoVoluntarioDcto5'] == True:
            sheet['K91'] = 'SÍ'
        else:
            sheet['K91'] = 'NO'
    
    if resultado['pagoVoluntarioMonto6'] is None:
        resultado['pagoVoluntarioMonto6'] = 0

    if resultado['pagoVoluntarioMonto6'] > 0:
        sheet['J92'] = resultado['pagoVoluntarioMonto6']
        if resultado['pagoVoluntarioDcto6'] == True:
            sheet['K92'] = 'SÍ'
        else:
            sheet['K92'] = 'NO'

  
     # Select the sheet with name "PRORRATEO"
    if "PRORRATEO" in workbook.sheetnames:
        prorrateo = workbook["PRORRATEO"]
    else:
        return HttpResponse("Sheet not found.", status=404)
    
    prorrateo['D6'] = resultado['mes0']
    prorrateo['d7'] = resultado['mes1']
    prorrateo['d8'] = resultado['mes2']
    prorrateo['d9'] = resultado['mes3']
    prorrateo['d10'] = resultado['mes4']
    prorrateo['d11'] = resultado['mes5']
    prorrateo['d12'] = resultado['mes6']
    prorrateo['d13'] = resultado['mes7']
    prorrateo['d14'] = resultado['mes8']
    prorrateo['d15'] = resultado['mes9']
    prorrateo['d16'] = resultado['mes10']
    prorrateo['d17'] = resultado['mes11']
    prorrateo['C6'] = resultado['primerMes']
    print('prmer mes', resultado['primerMes'])

  

       
    # Save the workbook to a temporary file
    temp_file = os.path.join(settings.BASE_DIR, 'static', 'temp_consultaFideicomiso.xlsx')
    workbook.save(temp_file)
    
    # Serve the file as a response
    nombre_cliente = resultado['nombreCliente']
    filename = f"Consulta - {numero_cotizacion} -{nombre_cliente}.xlsx"
    with open(temp_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

@login_required
def main_menu(request):
    return render(request, 'main_menu.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print('user', user, username, password)
        if user is not None:
            login(request, user)
            return redirect('main_menu')  # Redirect to the main menu after successful login
        else:
            messages.error(request, 'Invalid username or password')
            print('Invalid username or password')
    return render(request, 'registration/login.html')


@login_required
def fideicomiso_view(request):
    resultado = None
    if request.method == 'POST':
        form = FideicomisoForm(request.POST)
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
                print('Sucursal', sucursal)
                # Call the generarFideicomiso2 function
                params = {
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

                }
                #print('RESULTADO PARAMETROS', params)
                resultado = generarFideicomiso3(params)
                
                print("--------finalizado---------")
                resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra']/2,2) * 2
                # print in ta table format reusltado
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(resultado)

                #print(form.cleaned_data)
                #deserialize fechaCalculo in resultado
                resultado['fechaCalculo'] = resultado['fechaCalculo'].strftime('%Y-%m-%d')
                resultado['cotFechaInicioPago'] = resultado['cotFechaInicioPago'].strftime('%Y-%m-%d')
                resultado['calcFechaPromeCK'] = resultado['calcFechaPromeCK'].strftime('%Y-%m-%d')

                #PASE DE CAMPOS
                resultado['oficial'] = form.cleaned_data['oficial'] if form.cleaned_data['oficial'] is not None else "-"
                resultado['sucursal'] = form.cleaned_data['sucursal'] if form.cleaned_data['sucursal'] is not None else "-"
                resultado['sexo'] = sexo
                resultado['nombreCliente'] = form.cleaned_data['nombreCliente'] if form.cleaned_data['nombreCliente'] is not None else "-"
                resultado['cedulaCliente'] = form.cleaned_data['cedulaCliente'] if form.cleaned_data['cedulaCliente'] is not None else "-"
                resultado['calcComiCierreFinal'] = resultado['calcComiCierreFinal'] * 100
                
                resultado['tipoDocumento'] = form.cleaned_data['tipoDocumento'] if form.cleaned_data['tipoDocumento'] is not None else "-"
                resultado['apcScore'] = form.cleaned_data['apcScore'] if form.cleaned_data['apcScore'] is not None else 0
                resultado['apcPI'] = form.cleaned_data['apcPI'] / 100 if form.cleaned_data['apcPI'] is not None else 0
                resultado['valorAuto'] = form.cleaned_data['valorAuto'] if form.cleaned_data['valorAuto'] is not None else 0
                resultado['cotPlazoPago'] = auxPlazoPago if auxPlazoPago is not None else 0
                resultado['vendedor'] = form.cleaned_data['vendedor'] if form.cleaned_data['vendedor'] is not None else "-"
                #DATOS DEL AUTO
                resultado['marcaAuto'] = form.cleaned_data['marca'] if form.cleaned_data['marca'] is not None else "-"
                resultado['lineaAuto'] = form.cleaned_data['modelo'] if form.cleaned_data['modelo'] is not None else "-"
                resultado['yearAuto'] = form.cleaned_data['yearCarro'] if form.cleaned_data['yearCarro'] is not None else "-"
                resultado['montoMensualSeguro'] = montoMensualSeguro if montoMensualSeguro is not None else 0
                resultado['montoanualSeguro'] = montoanualSeguro if montoanualSeguro is not None else 0
                resultado['promoPublicidad'] = 50  # Assuming this is a fixed value
                resultado['transmision'] = form.cleaned_data['transmisionAuto'] if form.cleaned_data['transmisionAuto'] is not None else "AUTOMÁTICO"
                resultado['nuevoAuto'] = form.cleaned_data['nuevoAuto'] if form.cleaned_data['nuevoAuto'] is not None else "-"
                resultado['kilometrajeAuto'] = form.cleaned_data['kilometrajeAuto'] if form.cleaned_data['kilometrajeAuto'] is not None else 0
                resultado['observaciones'] = form.cleaned_data['observaciones'] if form.cleaned_data['observaciones'] is not None else "-"

                #Datos del deudor
                resultado['tiempoServicio'] = form.cleaned_data['tiempoServicio'] if form.cleaned_data['tiempoServicio'] is not None else "-"
                resultado['ingresos'] = form.cleaned_data['ingresos'] if form.cleaned_data['ingresos'] is not None else 0
                resultado['nombreEmpresa'] = form.cleaned_data['nombreEmpresa'] if form.cleaned_data['nombreEmpresa'] is not None else "-"
                resultado['referenciasAPC'] = form.cleaned_data['referenciasAPC'] if form.cleaned_data['referenciasAPC'] is not None else "-"
                resultado['cartera'] = form.cleaned_data['cartera'] if form.cleaned_data['cartera'] is not None else "-"
                resultado['licencia'] = form.cleaned_data['licencia'] if form.cleaned_data['licencia'] is not None else "-"
                resultado['posicion'] = form.cleaned_data['posicion'] if form.cleaned_data['posicion'] is not None else "-"
                resultado['perfilUniversitario'] = form.cleaned_data['perfilUniversitario'] if form.cleaned_data['perfilUniversitario'] is not None else "-"

                #DATOS NIVEL DE ENDEUDAMIENTO
                resultado['salarioBaseMensual'] = form.cleaned_data['salarioBaseMensual'] if form.cleaned_data['salarioBaseMensual'] is not None else 0
                resultado['horasExtrasMonto'] = form.cleaned_data['horasExtrasMonto'] if form.cleaned_data['horasExtrasMonto'] is not None else 0
                resultado['horasExtrasDcto'] = form.cleaned_data['horasExtrasDcto'] if form.cleaned_data['horasExtrasDcto'] is not None else 0
                resultado['primaMonto'] = form.cleaned_data['primaMonto'] if form.cleaned_data['primaMonto'] is not None else 0
                resultado['primaDcto'] = form.cleaned_data['primaDcto'] if form.cleaned_data['primaDcto'] is not None else 0
                resultado['bonosMonto'] = form.cleaned_data['bonosMonto'] if form.cleaned_data['bonosMonto'] is not None else 0
                resultado['bonosDcto'] = form.cleaned_data['bonosDcto'] if form.cleaned_data['bonosDcto'] is not None else 0
                resultado['otrosMonto'] = form.cleaned_data['otrosMonto'] if form.cleaned_data['otrosMonto'] is not None else 0
                resultado['otrosDcto'] = form.cleaned_data['otrosDcto'] if form.cleaned_data['otrosDcto'] is not None else 0

                #DESCUENTO DIRECTO
                resultado['siacapMonto'] = form.cleaned_data['siacapMonto'] if form.cleaned_data['siacapMonto'] is not None else 0
                resultado['siacapDcto'] = form.cleaned_data['siacapDcto'] if form.cleaned_data['siacapDcto'] is not None else False
                resultado['praaMonto'] = form.cleaned_data['praaMonto'] if form.cleaned_data['praaMonto'] is not None else 0
                resultado['praaDcto'] = form.cleaned_data['praaDcto'] if form.cleaned_data['praaDcto'] is not None else False
                resultado['dirOtrosMonto1'] = form.cleaned_data['dirOtrosMonto1'] if form.cleaned_data['dirOtrosMonto1'] is not None else 0
                resultado['dirOtros1'] = form.cleaned_data['dirOtros1'] if form.cleaned_data['dirOtros1'] is not None else "-"
                resultado['dirOtrosDcto1'] = form.cleaned_data['dirOtrosDcto1'] if form.cleaned_data['dirOtrosDcto1'] is not None else False
                resultado['dirOtrosMonto2'] = form.cleaned_data['dirOtrosMonto2'] if form.cleaned_data['dirOtrosMonto2'] is not None else 0
                resultado['dirOtros2'] = form.cleaned_data['dirOtros2'] if form.cleaned_data['dirOtros2'] is not None else "-"
                resultado['dirOtrosDcto2'] = form.cleaned_data['dirOtrosDcto2'] if form.cleaned_data['dirOtrosDcto2'] is not None else False
                resultado['dirOtrosMonto3'] = form.cleaned_data['dirOtrosMonto3'] if form.cleaned_data['dirOtrosMonto3'] is not None else 0
                resultado['dirOtros3'] = form.cleaned_data['dirOtros3'] if form.cleaned_data['dirOtros3'] is not None else "-"
                resultado['dirOtrosDcto3'] = form.cleaned_data['dirOtrosDcto3'] if form.cleaned_data['dirOtrosDcto3'] is not None else False
                resultado['dirOtrosMonto4'] = form.cleaned_data['dirOtrosMonto4'] if form.cleaned_data['dirOtrosMonto4'] is not None else 0
                resultado['dirOtros4'] = form.cleaned_data['dirOtros4'] if form.cleaned_data['dirOtros4'] is not None else "-"
                resultado['dirOtrosDcto4'] = form.cleaned_data['dirOtrosDcto4'] if form.cleaned_data['dirOtrosDcto4'] is not None else False


                #PAGO VOLUNTARIO
                resultado['pagoVoluntario1'] = form.cleaned_data['pagoVoluntario1'] if form.cleaned_data['pagoVoluntario1'] is not None else 0
                resultado['pagoVoluntarioMonto1'] = form.cleaned_data['pagoVoluntarioMonto1'] if form.cleaned_data['pagoVoluntarioMonto1'] is not None else 0
                resultado['pagoVoluntarioDcto1'] = form.cleaned_data['pagoVoluntarioDcto1'] if form.cleaned_data['pagoVoluntarioDcto1'] is not None else 0
                resultado['pagoVoluntario2'] = form.cleaned_data['pagoVoluntario2'] if form.cleaned_data['pagoVoluntario2'] is not None else 0
                resultado['pagoVoluntarioMonto2'] = form.cleaned_data['pagoVoluntarioMonto2'] if form.cleaned_data['pagoVoluntarioMonto2'] is not None else 0
                resultado['pagoVoluntarioDcto2'] = form.cleaned_data['pagoVoluntarioDcto2'] if form.cleaned_data['pagoVoluntarioDcto2'] is not None else 0
                resultado['pagoVoluntario3'] = form.cleaned_data['pagoVoluntario3'] if form.cleaned_data['pagoVoluntario3'] is not None else 0
                resultado['pagoVoluntarioMonto3'] = form.cleaned_data['pagoVoluntarioMonto3'] if form.cleaned_data['pagoVoluntarioMonto3'] is not None else 0
                resultado['pagoVoluntarioDcto3'] = form.cleaned_data['pagoVoluntarioDcto3'] if form.cleaned_data['pagoVoluntarioDcto3'] is not None else 0
                resultado['pagoVoluntario4'] = form.cleaned_data['pagoVoluntario4'] if form.cleaned_data['pagoVoluntario4'] is not None else 0
                resultado['pagoVoluntarioMonto4'] = form.cleaned_data['pagoVoluntarioMonto4'] if form.cleaned_data['pagoVoluntarioMonto4'] is not None else 0
                resultado['pagoVoluntarioDcto4'] = form.cleaned_data['pagoVoluntarioDcto4'] if form.cleaned_data['pagoVoluntarioDcto4'] is not None else 0
                resultado['pagoVoluntario5'] = form.cleaned_data['pagoVoluntario5'] if form.cleaned_data['pagoVoluntario5'] is not None else 0
                resultado['pagoVoluntarioMonto5'] = form.cleaned_data['pagoVoluntarioMonto5'] if form.cleaned_data['pagoVoluntarioMonto5'] is not None else 0
                resultado['pagoVoluntarioDcto5'] = form.cleaned_data['pagoVoluntarioDcto5'] if form.cleaned_data['pagoVoluntarioDcto5'] is not None else 0
                resultado['pagoVoluntario6'] = form.cleaned_data['pagoVoluntario6'] if form.cleaned_data['pagoVoluntario6'] is not None else 0
                resultado['pagoVoluntarioMonto6'] = form.cleaned_data['pagoVoluntarioMonto6'] if form.cleaned_data['pagoVoluntarioMonto6'] is not None else 0
                resultado['pagoVoluntarioDcto6'] = form.cleaned_data['pagoVoluntarioDcto6'] if form.cleaned_data['pagoVoluntarioDcto6'] is not None else 0
                
                resultado['horasExtrasMonto'] = form.cleaned_data['horasExtrasMonto'] if form.cleaned_data['horasExtrasMonto'] is not None else 0  
                #PRORRATEO
                resultado['mes0'] = form.cleaned_data['mes0'] if form.cleaned_data['mes0'] is not None else 0
                resultado['mes1'] = form.cleaned_data['mes1'] if form.cleaned_data['mes1'] is not None else 0
                resultado['mes2'] = form.cleaned_data['mes2'] if form.cleaned_data['mes2'] is not None else 0
                resultado['mes3'] = form.cleaned_data['mes3'] if form.cleaned_data['mes3'] is not None else 0
                resultado['mes4'] = form.cleaned_data['mes4'] if form.cleaned_data['mes4'] is not None else 0
                resultado['mes5'] = form.cleaned_data['mes5'] if form.cleaned_data['mes5'] is not None else 0
                resultado['mes6'] = form.cleaned_data['mes6'] if form.cleaned_data['mes6'] is not None else 0
                resultado['mes7'] = form.cleaned_data['mes7'] if form.cleaned_data['mes7'] is not None else 0
                resultado['mes8'] = form.cleaned_data['mes8'] if form.cleaned_data['mes8'] is not None else 0
                resultado['mes9'] = form.cleaned_data['mes9'] if form.cleaned_data['mes9'] is not None else 0
                resultado['mes10'] = form.cleaned_data['mes10'] if form.cleaned_data['mes10'] is not None else 0
                resultado['mes11'] = form.cleaned_data['mes11'] if form.cleaned_data['mes11'] is not None else 0
                resultado['primerMes'] = form.cleaned_data['primerMes'] if form.cleaned_data['primerMes'] is not None else ""
                resultado['tipoProrrateo'] = form.cleaned_data['tipoProrrateo'] if form.cleaned_data['tipoProrrateo'] is not None else ""
                print('primer mes', resultado['primerMes'],form.cleaned_data['primerMes'])
                
                # MONTO LETRA SIN SEGUROS
                resultado['wrkLetraSinSeguros'] = resultado['wrkMontoLetra']  - resultado['wrkLetraSeguro']
                resultado['wrkLetraSinSeguros'] = round(resultado['wrkLetraSinSeguros'], 2)
                resultado['wrkLetraConSeguros'] = resultado['wrkMontoLetra'] + resultado['montoMensualSeguro']
                resultado['wrkLetraConSeguros'] = round(resultado['wrkLetraConSeguros'], 2)
                resultado['calcComiCierreFinal'] = round(resultado['calcComiCierreFinal'], 2)
                resultado['montoLetraSeguroAdelantado'] =montoLetraSeguroAdelantado
                resultado['cashback'] = form.cleaned_data['cashback'] if form.cleaned_data['cashback'] is not None else 0
                resultado['cashback'] = round(resultado['cashback'], 2)
                resultado['r1']=round(resultado['r1'],2)
                resultado['abono'] = form.cleaned_data['abono'] if form.cleaned_data['abono'] is not None else 0
                resultado['abono'] = round(resultado['abono'], 2)
                resultado['abonoPorcentaje'] = form.cleaned_data['abonoPorcentaje'] if form.cleaned_data['abonoPorcentaje'] is not None else 0
                resultado['abonoPorcentaje'] = round(resultado['abonoPorcentaje'], 2)
                print('abonoporcentaje', resultado['abonoPorcentaje'])
                
                 # Convert Decimal fields to floats
                resultado = convert_decimal_to_float(resultado)
                #print('resultado despues de funcion------', resultado)
                #CALCULO NIVEL DE ENDEUDAMIENTO - REAL
                resultadoNivel = nivelEndeudamiento(resultado)
                resultado['salarioNeto'] = resultadoNivel['salarioNeto']
                resultado['porSalarioNeto'] = resultadoNivel['porSalarioNeto']
                resultado['salarioNetoActual'] = resultadoNivel['salarioNetoActual']
                resultado['totalIngresosAdicionales'] = resultadoNivel['totalIngresosAdicionales']
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

                pp.pprint(resultado)
                #save resultado['tasaEstimada'] in form instance
                form.instance.tasaEstimada = resultado['tasaEstimada']
                form.instance.tasaBruta = resultado['tasaBruta']
                form.instance.r1 = resultado['r1']
                form.instance.montoPrestamo = resultado['cotMontoPrestamo']
                form.instance.auxMonto2 = round(Decimal(resultado['auxMonto2']),2)
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
                form.instance.siacapMonto = resultado['siacapMonto']
                form.instance.siacapDcto = resultado['siacapDcto']
                form.instance.praaMonto = resultado['praaMonto']
                form.instance.praaDcto = resultado['praaDcto']
                #resultado nivel de endeuamiento - real
                form.instance.ingresos = resultado['ingresos']
                form.instance.horasExtrasMonto = resultado['horasExtrasMonto']
                form.instance.dirOtrosMonto1 = resultado['dirOtrosMonto1']
                form.instance.dirOtros1 = resultado['dirOtros1']
                form.instance.dirOtrosDcto1 = resultado['dirOtrosDcto1']
                form.instance.dirOtrosMonto2 = resultado['dirOtrosMonto2']
                form.instance.dirOtros2 = resultado['dirOtros2']
                form.instance.dirOtrosDcto2 = resultado['dirOtrosDcto2']
                form.instance.dirOtrosMonto3 = resultado['dirOtrosMonto3']
                form.instance.dirOtros3 = resultado['dirOtros3']
                form.instance.dirOtrosDcto3 = resultado['dirOtrosDcto3']
                form.instance.dirOtrosMonto4 = resultado['dirOtrosMonto4']
                form.instance.dirOtros4 = resultado['dirOtros4']
                form.instance.dirOtrosDcto4 = resultado['dirOtrosDcto4']
                form.instance.otrosDcto = resultado['otrosDcto']
                form.instance.pagoVoluntarioMonto1 = resultado['pagoVoluntarioMonto1']
                form.instance.pagoVoluntarioDcto1 = resultado['pagoVoluntarioDcto1']
                
                form.instance.pagoVoluntarioDcto2 = resultado['pagoVoluntarioDcto2']
                form.instance.pagoVoluntarioMonto3 = resultado['pagoVoluntarioMonto3']
                form.instance.pagoVoluntarioDcto3 = resultado['pagoVoluntarioDcto3']
                form.instance.pagoVoluntarioMonto4 = resultado['pagoVoluntarioMonto4']
                form.instance.pagoVoluntarioDcto4 = resultado['pagoVoluntarioDcto4']
                form.instance.pagoVoluntarioMonto5 = resultado['pagoVoluntarioMonto5']
                form.instance.pagoVoluntarioDcto5 = resultado['pagoVoluntarioDcto5']
                form.instance.pagoVoluntarioMonto6 = resultado['pagoVoluntarioMonto6']
                form.instance.pagoVoluntarioDcto6 = resultado['pagoVoluntarioDcto6']
                form.instance.pagoVoluntarioMonto2 = resultado['pagoVoluntarioMonto2']

                form.instance.mes0 = resultado['mes0']
                form.instance.mes1 = resultado['mes1']
                form.instance.mes2 = resultado['mes2']
                form.instance.mes3 = resultado['mes3']
                form.instance.mes4 = resultado['mes4']
                form.instance.mes5 = resultado['mes5']
                form.instance.mes6 = resultado['mes6']
                form.instance.mes7 = resultado['mes7']
                form.instance.mes8 = resultado['mes8']
                form.instance.mes9 = resultado['mes9']
                form.instance.mes10 = resultado['mes10']
                form.instance.mes11 = resultado['mes11']
                form.instance.primerMes = resultado['primerMes']
                form.instance.tipoProrrateo = resultado['tipoProrrateo']
                

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
                
                #------SAFE-------
                try:
                    #print form fields
                    #print all form fields in form instan
                    print("intentando guardar")
                    pp.pprint(form.cleaned_data)
                    form.save()
                    print("guardado")
                    # Get the NumeroCotizacion after saving the form
                    numero_cotizacion = form.instance.NumeroCotizacion
                    try:
                        resultado['numero_cotizacion'] = int(numero_cotizacion)
                    except:
                        resultado['numero_cotizacion'] = 0
                    print('NumeroCotizacion:', numero_cotizacion)
                    request.session['resultado'] = resultado

                    #return redirect('cotizacion_detail', pk=int(form.instance.NumeroCotizacion))
                    return render(request, 'fideicomiso_form.html', {'form': form, 'resultado': resultado})

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
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
    else:
        form = FideicomisoForm()
    
    return render(request, 'fideicomiso_form.html', {'form': form, 'resultado': resultado})
    