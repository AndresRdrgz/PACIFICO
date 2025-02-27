from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import FideicomisoForm, ClienteForm, AseguradoraForm
from .fideicomiso.fideicomiso import generarFideicomiso3, generarFideicomiso4
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
from .models import Cotizacion, Cliente, Aseguradora, UserProfile, CotizacionDocumento
import openpyxl
import pprint
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .viewsFideicomiso.cotizadorFideicomiso import perform_fideicomiso_calculation, prepResultado, aplicaCodeudor, set_calculated_values, convert_decimal_to_float, set_calculated_values2, calculoInicial
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from datetime import timedelta

from django.core.files.base import ContentFile
from reportlab.lib.units import inch
from io import BytesIO
import os
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger
from reportlab.lib.units import mm

from .filters import CotizacionFilter



# Get an instance of a logger
logger = logging.getLogger(__name__)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'

def log_error(error_message, username):
    # Define the directory where you want to save the error logs
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a unique filename based on the current timestamp and username
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'error_log_{username}_{timestamp}.txt'
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Configure logging
    logging.basicConfig(filename=log_filepath, level=logging.ERROR)
    
    # Log the error message
    logging.error(error_message)

def download_merged_pdf(request, numero_cotizacion):
    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=numero_cotizacion)
    documentos = CotizacionDocumento.objects.filter(cotizacion=cotizacion)

    merger = PdfMerger()

    for documento in documentos:
        if documento.documento.path.endswith('.pdf'):
            merger.append(documento.documento.path)

    # Create a new PDF with A4 size
    a4_width = 210 * mm
    a4_height = 297 * mm
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=(a4_width, a4_height))

    # Save the merged PDF to a file
    merged_pdf_path = os.path.join(settings.MEDIA_ROOT, f'cotizacion_{numero_cotizacion}_merged.pdf')
    merger.write(merged_pdf_path)
    merger.close()

    with open(merged_pdf_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cotizacion_{numero_cotizacion}_merged.pdf"'

    return response

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
            last_activity = data.get('last_activity', None)
            user_sessions.append({
                'username': user.username,
                'session_key': session.session_key,
                'expire_date': session.expire_date,
                'email': user.email,
                'last_activity': last_activity
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
    original_numero = cotizacion.NumeroCotizacion  # Store original number
   
    form = FideicomisoForm(instance=cotizacion)
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
        form = FideicomisoForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            try:
                aseguradora = form.cleaned_data['aseguradora']
                form_data = form.cleaned_data
                resultado = perform_fideicomiso_calculation(form)

                # Create a new form instance to save a new record
                new_form = FideicomisoForm(request.POST)
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



def download_cotizaciones_excel(request):
    cotizaciones = Cotizacion.objects.all()

    # Filter cotizaciones by addedBy current user
    if request.user.is_authenticated and not request.user.is_staff:
        cotizaciones = cotizaciones.filter(added_by=request.user)
        
    cotizaciones = cotizaciones.order_by('-created_at')

    # Create an in-memory workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Cotizaciones"
    
    # Define the headers
    headers = [
        "ID","Fecha Cotizacion", "Oficial", "Sucursal", "Nombre Cliente", "Cédula Cliente", "Fecha Nacimiento", "Edad", "Sexo", 
        "Jubilado", "Patrono", "Patrono Código", "Vendedor", "Vendedor Comisión", "Aseguradora", "Tasa Bruta", 
        "Marca", "Modelo", "Fecha Inicio Pago", "Monto Préstamo", "Comisión Cierre", 
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
            cotizacion.created_at.replace(tzinfo=None),
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

    # Filter cotizaciones by addedBy current user
    if request.user.is_authenticated:
        cotizaciones = cotizaciones.filter(added_by=request.user)

    # If user is staff show all cotizaciones
    if request.user.is_staff:
        cotizaciones = Cotizacion.objects.all()

    # Sort by newest first
    cotizaciones = cotizaciones.order_by('-created_at')

    # Get all cotizaciones done in the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    cotizaciones_last_30_days = cotizaciones.filter(created_at__range=[start_date, end_date])

    # Aggregate cotizaciones by day
    cotizaciones_by_day = cotizaciones_last_30_days.extra({'day': "date(created_at)"}).values('day').annotate(count=Count('id')).order_by('day')

    # Prepare data for the chart
    dates = [entry['day'] for entry in cotizaciones_by_day]
    counts = [entry['count'] for entry in cotizaciones_by_day]

    context = {
        'cotizaciones': cotizaciones,
        'dates': dates,
        'counts': counts,
    }

    return render(request, 'cotizacionesList.html', context)

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
def main_menu(request):
    if request.user.is_authenticated and not request.user.is_staff:
        cotizaciones = Cotizacion.objects.filter(added_by=request.user)
    else:
        cotizaciones = Cotizacion.objects.all()
    
    # Apply filters
    cotizacion_filter = CotizacionFilter(request.GET, queryset=cotizaciones)
    filtered_cotizaciones = cotizacion_filter.qs

    # Filter by created_at and get only the past 15 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    filtered_cotizaciones = filtered_cotizaciones.filter(created_at__range=[start_date, end_date]).order_by('created_at')

    cotizaciones_data = [
        {
            'numeroCotizacion': cotizacion.NumeroCotizacion if cotizacion.NumeroCotizacion is not None else "-",
            'nombreCliente': cotizacion.nombreCliente if cotizacion.nombreCliente is not None else "-",
            'cedulaCliente': cotizacion.cedulaCliente if cotizacion.cedulaCliente is not None else "-",
            'sucursal': cotizacion.sucursal if cotizacion.sucursal is not None else "-",
            'oficial': cotizacion.oficial if cotizacion.oficial is not None else "-",
            'FechaCreacion': cotizacion.created_at.strftime('%Y-%m-%d'),
            'Vendedor': cotizacion.vendedor if cotizacion.vendedor is not None else "-",
            'marca': cotizacion.marca if cotizacion.marca is not None else "-",
            'modelo': cotizacion.modelo if cotizacion.modelo is not None else "-",
            'cartera': cotizacion.cartera if cotizacion.cartera is not None else "-",
            'montoPrestamo': float(cotizacion.montoPrestamo) if cotizacion.montoPrestamo is not None else 0.0,
        }
        for cotizacion in filtered_cotizaciones
    ]

    context = {
        'cotizaciones_data': cotizaciones_data,
        'filter': cotizacion_filter,
        'is_staff': request.user.is_staff,
        'username': request.user.username,
        'user_profile': UserProfile.objects.get(user=request.user),
        'full_name': f"{request.user.first_name} {request.user.last_name}",
    }
    
    return render(request, 'main_menu.html', context)

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
        form = FideicomisoForm(request.POST, request.FILES)
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
                

                
                resultado['lineaAuto'] = form.cleaned_data.get('lineaAuto', '-')
                form.instance.lineaAuto = resultado['lineaAuto']
   
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
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
    else:
        form = FideicomisoForm()
    
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

    return render(request, 'fideicomiso_form.html', context)


@login_required
def calculoAppx(request):
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
                calcTasaInteres = form.cleaned_data['tasaInteres'] / 100
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
                #print('Sucursal', sucursal)
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
                resultado, iteration_data = generarFideicomiso4(params)
                
                print("--------finalizado---------")
                resultado['wrkMontoLetra'] = round(resultado['wrkMontoLetra']/2,2) * 2
                # print in ta table format reusltado
               

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
                
                resultado['nuevoAuto'] = form.cleaned_data['nuevoAuto'] if form.cleaned_data['nuevoAuto'] is not None else "-"
                resultado['kilometrajeAuto'] = form.cleaned_data['kilometrajeAuto'] if form.cleaned_data['kilometrajeAuto'] is not None else 0
                resultado['observaciones'] = form.cleaned_data['observaciones'] if form.cleaned_data['observaciones'] is not None else "-"
  
                
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
                #print('abonoporcentaje', resultado['abonoPorcentaje'])
                
                 # Convert Decimal fields to floats
                resultado = convert_decimal_to_float(resultado)
                #print('resultado despues de funcion------', resultado)
               
                
                

                
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
                

                
                resultado['lineaAuto'] = form.cleaned_data.get('lineaAuto', '-')
                form.instance.lineaAuto = resultado['lineaAuto']
   
                
                form.instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
            
                return render(request, 'calculoAppx.html', {'form': form, 'resultado': resultado,
                                                            'iteration_data': iteration_data})
            
            except Exception as e:
                logger.error("Error in fideicomiso_view: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
                print(e)
     
        else:
            logger.warning("Form is not valid: %s", form.errors)
            print(form.errors)
    else:
        form = FideicomisoForm()
    
    #check user sucursal, is not none set form.sucursal to user.sucursal
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.sucursal is not None:
            form.fields['sucursal'].initial = user_profile.sucursal
        
        if user_profile.oficial is not None:
            form.fields['oficial'].initial = user_profile.oficial
    

    return render(request, 'calculoAppx.html', {'form': form, 'resultado': resultado
                                                })
    
@login_required
def reportesDashboard(request):
    cotizaciones = Cotizacion.objects.all()
    cotizacion_filter = CotizacionFilter(request.GET, queryset=cotizaciones)
    filtered_cotizaciones = cotizacion_filter.qs

    cotizaciones_data = [
        {
            'numeroCotizacion': cotizacion.NumeroCotizacion,
            'nombreCliente': cotizacion.nombreCliente,
            'cedulaCliente': cotizacion.cedulaCliente,
            'sucursal': cotizacion.sucursal,
            'oficial': cotizacion.oficial,
            'FechaCreacion': cotizacion.created_at.strftime('%Y-%m-%d'),
            'vendedor': cotizacion.vendedor,
            'Marca': cotizacion.marca,
            'Modelo': cotizacion.modelo,
        }
        for cotizacion in filtered_cotizaciones
    ]

    context = {
        'cotizaciones': cotizaciones_data,
        'filter': cotizacion_filter,
    }

    return render(request, 'reportesDashboard.html', context)