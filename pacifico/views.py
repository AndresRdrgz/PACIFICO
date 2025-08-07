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

@login_required
def update_consulta_fields(request, numero_cotizacion):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    cotizacion = get_object_or_404(Cotizacion, NumeroCotizacion=numero_cotizacion)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    sector = data.get('sector')
    politica_id = data.get('politica')
    observaciones = data.get('observaciones')
    tiempo_servicio = data.get('tiempoServicio')
    nombre_empresa = data.get('nombreEmpresa')
    ingresos = data.get('ingresos')
    posicion = data.get('posicion')
    apc_score = data.get('apcScore')
    apc_pi = data.get('apcPI')

    # Basic validation
    missing = []
    if not sector:
        missing.append('sector')
    if not politica_id:
        missing.append('politica')
    if not observaciones:
        missing.append('observaciones')
    # New required fields
    if not tiempo_servicio:
        missing.append('tiempoServicio')
    if not nombre_empresa:
        missing.append('nombreEmpresa')
    if not ingresos:
        missing.append('ingresos')
    if not posicion:
        missing.append('posicion')
    if apc_score in (None, ""):
        missing.append('apcScore')
    if apc_pi in (None, ""):
        missing.append('apcPI')

    if missing:
        return JsonResponse({'ok': False, 'missing': missing, 'error': 'Campos requeridos faltantes'}, status=400)

    # Update model
    from .models import Politicas
    try:
        politica = Politicas.objects.get(pk=politica_id)
    except Politicas.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Política inválida'}, status=400)

    # Type conversions with validation
    from decimal import Decimal as _Dec
    def to_int(val, field):
        try:
            return int(str(val).strip())
        except Exception:
            raise ValueError(f"{field} inválido")
    def to_dec(val, field):
        try:
            return _Dec(str(val).strip())
        except Exception:
            raise ValueError(f"{field} inválido")

    try:
        cotizacion.sector = sector
        cotizacion.politica = politica
        cotizacion.observaciones = observaciones
        cotizacion.tiempoServicio = tiempo_servicio.strip()  # Keep as text, just strip whitespace
        cotizacion.nombreEmpresa = nombre_empresa
        cotizacion.ingresos = to_dec(ingresos, 'Ingresos')
        cotizacion.posicion = posicion
        cotizacion.apcScore = to_int(apc_score, 'APC Score')
        cotizacion.apcPI = to_dec(apc_pi, 'APC PI')
        cotizacion.save(update_fields=['sector', 'politica', 'observaciones', 'tiempoServicio', 'nombreEmpresa', 'ingresos', 'posicion', 'apcScore', 'apcPI'])
    except ValueError as ve:
        return JsonResponse({'ok': False, 'error': str(ve)}, status=400)

    return JsonResponse({'ok': True})

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
                        'tipoPrestamo' : form.cleaned_data['tipoPrestamo'],

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
                    new_form.instance.cototalIngresosAdicionales = round(resultadoNivelCodeudor['totalIngresosAdicionales'], 2)
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
                #print data type of totalIngresosAdicionales
                print(type(resultado['totalIngresosAdicionales']))
                #new_form.instance.totalIngresosAdicionales = round(resultado['totalIngresosAdicionales'] if resultado['totalIngresosAdicionales'] is not None else 0, 2)
                new_form.instance.totalIngresosMensualesCompleto = resultado['totalIngresosMensualesCompleto']
                new_form.instance.totalDescuentosLegalesCompleto = resultado['totalDescuentosLegalesCompleto']
                new_form.instance.salarioNetoActualCompleto = resultado['salarioNetoActualCompleto']
                new_form.instance.salarioNetoCompleto = resultado['salarioNetoCompleto']
                new_form.instance.porSalarioNetoCompleto = resultado['porSalarioNetoCompleto']
                # ------------------- Save the new record -------------------
                print("intentando guardar","totalIngresosAdicionales",resultado['totalIngresosAdicionales'])            
                if new_form.is_valid():
                    print("formulario es valido")
                    new_instance = new_form.save(commit=False)
                    new_instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                    new_instance.tipoPrestamo = 'auto'
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
                    new_instance.totalIngresosAdicionales = round(resultado['totalIngresosAdicionales'],2)
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
                    new_instance.tipoPrestamo = 'auto'
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
                    
                    print("aNew form is not valid: %s", new_form.errors)
                    #print all fields of new_form
                    for field in new_form:
                        print(f"{field.name}: {field.value()}")
                    
                    context['errors'] = f"New form is not valid: {new_form.errors}"
                    log_error(f"New form is not valid: {new_form.errors}", request.user.username)
                    
                    

            except Exception as e:
                print('Error:', e)
                error_message = str(e)
                log_error(error_message, request.user.username)
                #context['errors'] = 'Error:' + error_message
                pass
                
        else:
            logger.warning("Form is not valid: %s", form.errors)
            #add to context the errors
            context['errors'] = form.errors
            print(form.errors)
            
            
    return render(request, 'fideicomiso_form.html', context)



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


def download_cotizaciones_json(request):
    cotizaciones = Cotizacion.objects.all()

    # Filter cotizaciones by addedBy current user
    if request.user.is_authenticated and not request.user.is_staff:
        cotizaciones = cotizaciones.filter(added_by=request.user)
        
    cotizaciones = cotizaciones.order_by('-created_at')

    # Serialize the data
    cotizaciones_data = [
        {
            "ID": cotizacion.id,
            "Fecha Cotizacion": cotizacion.created_at.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S'),
            "Oficial": cotizacion.oficial,
            "Sucursal": cotizacion.sucursal,
            "Nombre Cliente": cotizacion.nombreCliente,
            "Cédula Cliente": cotizacion.cedulaCliente,
            "Fecha Nacimiento": cotizacion.fechaNacimiento.strftime('%Y-%m-%d') if cotizacion.fechaNacimiento else None,
            "Edad": cotizacion.edad,
            "Sexo": cotizacion.sexo,
            "Jubilado": cotizacion.jubilado,
            "Patrono": cotizacion.patrono,
            "Patrono Código": cotizacion.patronoCodigo,
            "Vendedor": cotizacion.vendedor,
            "Vendedor Comisión": cotizacion.vendedorComision,
            "Aseguradora": str(cotizacion.aseguradora),  # Convert aseguradora to string
            "Tasa Bruta": cotizacion.tasaBruta,
            "Marca": cotizacion.marca,
            "Modelo": cotizacion.modelo,
            "Fecha Inicio Pago": cotizacion.fechaInicioPago.strftime('%Y-%m-%d') if cotizacion.fechaInicioPago else None,
            "Monto Préstamo": cotizacion.montoPrestamo,
            "Comisión Cierre": cotizacion.comiCierre,
            "Comisión Cierre Final": cotizacion.calcComiCierreFinal,
            "Plazo Pago": cotizacion.plazoPago,
            "R Deseada": cotizacion.r_deseada,
            "Tasa Estimada": cotizacion.tasaEstimada,
            "R1": cotizacion.r1,
            "Monto 2": cotizacion.auxMonto2,
            "Monto Letra": cotizacion.wrkMontoLetra,
            "Monto Notaría": cotizacion.calcMontoNotaria,
            "Monto Timbres": cotizacion.calcMontoTimbres,
            "Manejo 5%": cotizacion.manejo_5porc,
            "Total Pagos": cotizacion.tablaTotalPagos,
            "Total Seguro": cotizacion.tablaTotalSeguro,
            "Total Feci": cotizacion.tablaTotalFeci,
            "Total Interés": cotizacion.tablaTotalInteres,
            "Total Monto Capital": cotizacion.tablaTotalMontoCapital,
        }
        for cotizacion in cotizaciones
    ]

    # Return the data as a JSON response
    return JsonResponse(cotizaciones_data, safe=False)

@login_required
def cotizacionesList(request):
    cotizaciones = Cotizacion.objects.all()
    cotizacion_filter = CotizacionFilter(request.GET, queryset=cotizaciones)

    filtered_cotizaciones = cotizacion_filter.qs

    # Filter cotizaciones by addedBy current user
    if request.user.is_authenticated and not request.user.is_staff:
        filtered_cotizaciones = filtered_cotizaciones.filter(added_by=request.user)

    # Filter by the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    filtered_cotizaciones = filtered_cotizaciones.filter(created_at__range=[start_date, end_date])

    # Sort by newest first
    filtered_cotizaciones = filtered_cotizaciones.order_by('-created_at')
    
    context = {
        'cotizaciones': filtered_cotizaciones,
        'filter': cotizacion_filter,
    }

    return render(request, 'cotizacionesListv2.html', context)


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
                quinVende = form.cleaned_data['quinVende'] if form.cleaned_data['quinVende'] is not None else "-"
                marcaAuto = form.cleaned_data['marcaAuto'] if form.cleaned_data['marcaAuto'] is not None else "-"
                print('marcaAuto', marcaAuto, 'quinVende', quinVende)
               
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
                    'quinVende': quinVende,
                    'marcaAuto': marcaAuto,

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
                    'selectDescuento': selectDescuento,
                    'porServDesc': porServDesc,
                    'pagaDiciembre': pagaDiciembre,

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
                #resultado['lineaAuto'] = form.cleaned_data['modelo'] if form.cleaned_data['modelo'] is not None else "-"
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
                

                
                #resultado['lineaAuto'] = form.cleaned_data.get('lineaAuto', '-')
                #form.instance.lineaAuto = resultado['lineaAuto']
   
                
                form.instance.added_by = request.user if request.user.is_authenticated else "INVITADO"
                form.instance.tipoPrestamo = 'auto'
            
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


@csrf_exempt
@login_required
def makito_rpa_request(request):
    """
    Handle Makito RPA automation requests
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        import json
        from django.core.mail import send_mail
        from django.conf import settings
        import uuid
        from datetime import datetime
        
        data = json.loads(request.body)
        service_type = data.get('serviceType')
        
        # Validate required fields
        if not service_type:
            return JsonResponse({'success': False, 'error': 'Tipo de servicio requerido'})
        
        # Generate unique request code
        request_code = f"MAKITO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Prepare email data based on service type
        subject_codes = {
            'apc': 'cot_APC',
            'sura': 'cot_SURA',
            'debida_diligencia': 'cot_DebidaDiligencia'
        }
        
        subject = f"{subject_codes.get(service_type, 'cot_UNKNOWN')} - {request_code}"
        
        # Build email body with structured data for regex extraction
        email_body = """
==========================================
DATOS PARA EXTRACCIÓN AUTOMATIZADA (MAKITO RPA)
==========================================
"""
        
        # Add common fields
        email_body += f"<codigoSolicitudvar>{request_code}</codigoSolicitudvar>\n"
        email_body += f"<numeroDocumentovar>{data.get('noDocumento', '')}</numeroDocumentovar>\n"
        email_body += f"<tipoDocumentovar>{data.get('tipoDocumento', '')}</tipoDocumentovar>\n"
        email_body += f"<usuarioSolicitantevar>{request.user.email}</usuarioSolicitantevar>\n"
        email_body += f"<tipoServiciovar>{service_type}</tipoServiciovar>\n"
        
        # Add service-specific fields
        if service_type == 'sura':
            email_body += f"<primerNombrevar>{data.get('primerNombre', '')}</primerNombrevar>\n"
            email_body += f"<segundoNombrevar>{data.get('segundoNombre', '')}</segundoNombrevar>\n"
            email_body += f"<primerApellidovar>{data.get('primerApellido', '')}</primerApellidovar>\n"
            email_body += f"<segundoApellidovar>{data.get('segundoApellido', '')}</segundoApellidovar>\n"
            
            # Create client name
            nombres = [data.get('primerNombre', ''), data.get('segundoNombre', '')]
            apellidos = [data.get('primerApellido', ''), data.get('segundoApellido', '')]
            cliente_completo = ' '.join([n for n in nombres if n]) + ' ' + ' '.join([a for a in apellidos if a])
            
            email_body += f"<clientevar>{cliente_completo.strip()}</clientevar>\n"
            email_body += f"<valorAutovar>{data.get('valorAuto', '')}</valorAutovar>\n"
            email_body += f"<anoAutovar>{data.get('anoAuto', '')}</anoAutovar>\n"
            email_body += f"<marcaAutovar>{data.get('marcaAuto', '')}</marcaAutovar>\n"
            email_body += f"<modeloAutovar>{data.get('modeloAuto', '')}</modeloAutovar>\n"
            
        elif service_type == 'debida_diligencia':
            email_body += f"<clientevar>{data.get('nombreCompleto', '')}</clientevar>\n"
        
        elif service_type == 'apc':
            # For APC, we only need the document info which is already added above
            pass
        
        email_body += """
==========================================
INSTRUCCIONES PARA MAKITO RPA:
==========================================
"""
        
        if service_type == 'apc':
            email_body += """
- Proceso: Solicitar descarga de APC
- Documento requerido: Reporte APC del cliente
- Extraer información de buró de crédito
- Enviar resultado al usuario solicitante
"""
        elif service_type == 'sura':
            email_body += """
- Proceso: Cotizar póliza de seguro de auto con SURA
- Cotizar cobertura de seguro vehicular
- Incluir todas las coberturas disponibles
- Enviar cotización completa al usuario solicitante
"""
        elif service_type == 'debida_diligencia':
            email_body += """
- Proceso: Realizar debida diligencia del cliente
- Verificar información en bases de datos públicas
- Buscar antecedentes y referencias
- Compilar reporte de debida diligencia
- Enviar reporte al usuario solicitante
"""
        
        email_body += f"""
==========================================
DATOS DE CONTACTO:
==========================================
Usuario solicitante: {request.user.get_full_name() or request.user.username}
Email del usuario: {request.user.email}
Fecha de solicitud: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==========================================
"""
        
        # Send email to Makito RPA
        try:
            from django.core.mail import send_mail
            
            # Send to main recipient
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['makito@fpacifico.com'],
                fail_silently=False,
            )
            
            # Send CC copy
            send_mail(
                subject=f"[COPIA] {subject}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['arodriguez@fpacifico.com', 'jacastillo@fpacifico.com'],
                fail_silently=True,  # Don't fail if CC emails fail
            )
            
            # Log the request
            logger.info(f"Makito RPA request sent - Type: {service_type}, User: {request.user.username}, Code: {request_code}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Solicitud enviada exitosamente a Makito RPA',
                'request_code': request_code
            })
            
        except Exception as email_error:
            logger.error(f"Error sending Makito RPA email: {str(email_error)}")
            return JsonResponse({
                'success': False, 
                'error': f'Error enviando email: {str(email_error)}'
            })
    
    except Exception as e:
        logger.error(f"Error processing Makito RPA request: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': f'Error procesando solicitud: {str(e)}'
        })