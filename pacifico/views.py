from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import FideicomisoForm
from .fideicomiso.fideicomiso import generarFideicomiso2  # Corrected import statement
import datetime
import logging
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from openpyxl import load_workbook
import os
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)

#@login_required
def generate_report(request):
    # Path to the static Excel file
    excel_path = os.path.join(settings.BASE_DIR, 'static', 'consultaFideicomiso.xlsx')

    if not os.path.exists(excel_path):
        return HttpResponse("File not found.", status=404)
    # Load the workbook and select the active sheet
    workbook = load_workbook(excel_path)
    sheet = workbook.active
    # Select the sheet with name "COTIZADOR LEASING"
    if "COTIZADOR LEASING" in workbook.sheetnames:
        sheet = workbook["COTIZADOR LEASING"]
    else:
        return HttpResponse("Sheet not found.", status=404)

    # Example values calculated in fideicomiso_view
    edad = 30
    sexo = 'Masculino'
    monto_prestamo = 100000
    tasa_interes = 0.10
    comision_cierre = 0.02
    plazo_pago = 12
    patrono = 'Patrono Example'
    sucursal = 13
    periocidad = 1
    forma_pago = 4
    aseguradora = 'Aseguradora Example'
    r_deseada = 0.05
    comision_vendedor = 0.03
    financia_seguro = True
    meses_financia_seguro = 12
    monto_anual_seguro = 1200
    monto_mensual_seguro = 100

    # Fill in the cells with the calculated values
    sheet['I10'] = sexo

    # Ensure the media directory exists
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    # Save the workbook to a temporary file
    temp_file = os.path.join(settings.MEDIA_ROOT, 'temp_report.xlsx')
    workbook.save(temp_file)

    # Serve the file as a response
    with open(temp_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=consultaFideicomiso.xlsx'
        return response

#@login_required
def main_menu(request):
    return render(request, 'main_menu.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_menu')  # Redirect to the main menu after successful login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'registration/login.html')

#@login_required
def fideicomiso_view(request):
    resultado = None
    if request.method == 'POST':
        form = FideicomisoForm(request.POST)
        if form.is_valid():
            try:
                # Extract form data
                edad = form.cleaned_data['edad']
                sexo = form.cleaned_data['sexo']
                cotMontoPrestamo = Decimal(form.cleaned_data['montoPrestamo'])
                calcTasaInteres = 10 / 100
                calcComiCierre = Decimal(form.cleaned_data['comiCierre']) / Decimal(100)
                auxPlazoPago = form.cleaned_data['plazoPago']
                patrono = form.cleaned_data['patronoCodigo']
                sucursal = 13
                auxPeriocidad = 1
                forma_pago = 4
                #COLECTIVO DE CREDITO
                aseguradora = form.cleaned_data['aseguradora']
                print('aseguradora', aseguradora)
                codigoSeguro = aseguradora.codigo
                r_deseada = Decimal(form.cleaned_data['r_deseada']) / Decimal(100)
                comisionVendedor = form.cleaned_data['vendedorComision']
                #CAMPOS SEGURO AUTO
                financiaSeguro = form.cleaned_data['financiaSeguro']
                mesesFinanciaSeguro = form.cleaned_data['mesesFinanciaSeguro']
                montoanualSeguro = form.cleaned_data['montoanualSeguro']
                montoMensualSeguro = form.cleaned_data['montoMensualSeguro']
                cantPagosSeguro = form.cleaned_data['cantPagosSeguro']

                
                #parse cotMontoPRestamo to float
                cotMontoPrestamo = float(cotMontoPrestamo)
                calcTasaInteres = float(calcTasaInteres)
                calcComiCierre = float(calcComiCierre)
                r_deseada = float(r_deseada)
                comisionVendedor = float(comisionVendedor)
                montoanualSeguro = float(montoanualSeguro)
                montoMensualSeguro = float(montoMensualSeguro)
                
                # Call the generarFideicomiso2 function
                params = {
                    'edad': edad,
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
                    'cantPagosSeguro': cantPagosSeguro

                }
                print('params', params)
                resultado = generarFideicomiso2(params)
            except Exception as e:
                logger.error("Error in fideicomiso_view: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
        else:
            logger.warning("Form is not valid: %s", form.errors)
    else:
        form = FideicomisoForm()
    
    return render(request, 'fideicomiso_form.html', {'form': form, 'resultado': resultado})