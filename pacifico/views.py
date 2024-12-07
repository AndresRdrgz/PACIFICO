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
from django.http import JsonResponse
import json
from pathlib import Path




# Get an instance of a logger
logger = logging.getLogger(__name__)

def convert_decimal_to_float(data):
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
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

#@login_required
def generate_report(request):
    # Retrieve the result from the session
    resultado = request.session.get('resultado')
    #print(resultado)
    
    if not resultado:
        return HttpResponse("No data found.", status=404)
    
    # Path to the static Excel file
    excel_path = os.path.join(settings.BASE_DIR, 'static/insumos', 'consultaFideicomiso.xlsx')

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
    
    # Example: Write the resultado data to the Excel sheet
    sheet['D6'] =resultado['oficial']
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
    sheet['J78']=resultado['horasExtrasMonto']

    #DESCUENTO DIRECTO
    sheet['E87'] = resultado['siacapMonto']
    sheet['e88'] = resultado['praaMonto']
    sheet['e89'] = resultado['dirOtrosMonto1']
    sheet['e90'] = resultado['dirOtrosMonto2']
    sheet['e91'] = resultado['dirOtrosMonto3']
    sheet['e92'] = resultado['dirOtrosMonto4']
    sheet['C89'] = resultado['dirOtros1']
    sheet['C90'] = resultado['dirOtros2']
    sheet['C91'] = resultado['dirOtros3']
    sheet['C92'] = resultado['dirOtros4']
    if resultado['siacapDcto'] == True:
        sheet['F87'] = 'SÍ'
    else:
        sheet['F87'] = 'NO'
    if resultado['praaDcto'] == True:
        sheet['F88'] = 'SÍ'
    else:
        sheet['F88'] = 'NO'
    if resultado['dirOtrosDcto1'] == True:
        sheet['F89'] = 'SÍ'
    else:
        sheet['F89'] = 'NO'
    if resultado['dirOtrosDcto2'] == True:
        sheet['F90'] = 'SÍ'
    else:
        sheet['F90'] = 'NO'
    if resultado['dirOtrosDcto3'] == True:
        sheet['F91'] = 'SÍ'
    else:
        sheet['F91'] = 'NO'
    if resultado['dirOtrosDcto4'] == True:
        sheet['f92'] = 'SÍ'
    else:
        sheet['f92'] = 'NO'
    #pagos voluntarios
    sheet['H87'] = resultado['pagoVoluntario1']
    sheet['J87'] = resultado['pagoVoluntarioMonto1']
    sheet['H88'] = resultado['pagoVoluntario2']
    sheet['J88'] = resultado['pagoVoluntarioMonto2']
    sheet['H89'] = resultado['pagoVoluntario3']
    sheet['J89'] = resultado['pagoVoluntarioMonto3']
    sheet['H90'] = resultado['pagoVoluntario4']
    sheet['J90'] = resultado['pagoVoluntarioMonto4']
    sheet['H91'] = resultado['pagoVoluntario5']
    sheet['J91'] = resultado['pagoVoluntarioMonto5']
    sheet['H92'] = resultado['pagoVoluntario6']
    sheet['J92'] = resultado['pagoVoluntarioMonto6']
       

    #PARSE TRUE TO SI AND FALSE TO NO
    if resultado['pagoVoluntarioDcto1'] == True:
        sheet['K87'] = 'SÍ'
    else:
        sheet['K87'] = 'NO'
    if resultado['pagoVoluntarioDcto2'] == True:
        sheet['K88'] = 'SÍ'
    else:
        sheet['K88'] = 'NO'
    if resultado['pagoVoluntarioDcto3'] == True:
        sheet['K89'] = 'SÍ'
    else:
        sheet['K89'] = 'NO'
    if resultado['pagoVoluntarioDcto4'] == True:
            sheet['K90'] = 'SÍ'
    else:
            sheet['K90'] = 'NO'
    if resultado['pagoVoluntarioDcto5'] == True:
            sheet['K91'] = 'SÍ'
    else:
            sheet['K91'] = 'NO'
    if resultado['pagoVoluntarioDcto6'] == True:
            sheet['K92'] = 'SÍ'
    else:
            sheet['K92'] = 'NO'
  
    
       
    # Save the workbook to a temporary file
    temp_file = os.path.join(settings.BASE_DIR, 'static', 'temp_consultaFideicomiso.xlsx')
    workbook.save(temp_file)
    
    # Serve the file as a response
    nombre_cliente = resultado['nombreCliente']
    filename = f"Consulta - {nombre_cliente}.xlsx"
    with open(temp_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
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
                nombreCliente = form.cleaned_data['nombreCliente']
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
                #print('RESULTADO PARAMETROS', params)
                resultado = generarFideicomiso2(params)
                #print("--------finalizado---------")
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
                resultado['apcScore'] = form.cleaned_data['apcScore'] if form.cleaned_data['apcScore'] is not None else "-"
                resultado['apcPI'] = form.cleaned_data['apcPI'] / 100 if form.cleaned_data['apcPI'] is not None else 0
                resultado['valorAuto'] = form.cleaned_data['valorAuto'] if form.cleaned_data['valorAuto'] is not None else 0
                resultado['cotPlazoPago'] = auxPlazoPago if auxPlazoPago is not None else 0
                resultado['vendedor'] = form.cleaned_data['vendedor'] if form.cleaned_data['vendedor'] is not None else "-"
                #DATOS DEL AUTO
                resultado['marcaAuto'] = form.cleaned_data['marcaAuto'] if form.cleaned_data['marcaAuto'] is not None else "-"
                resultado['lineaAuto'] = form.cleaned_data['lineaAuto'] if form.cleaned_data['lineaAuto'] is not None else "-"
                resultado['yearAuto'] = form.cleaned_data['yearAuto'] if form.cleaned_data['yearAuto'] is not None else "-"
                resultado['montoMensualSeguro'] = montoMensualSeguro if montoMensualSeguro is not None else 0
                resultado['montoanualSeguro'] = montoanualSeguro if montoanualSeguro is not None else 0
                resultado['promoPublicidad'] = 50  # Assuming this is a fixed value
                resultado['transmision'] = form.cleaned_data['transmisionAuto'] if form.cleaned_data['transmisionAuto'] is not None else "-"
                resultado['nuevoAuto'] = form.cleaned_data['nuevoAuto'] if form.cleaned_data['nuevoAuto'] is not None else "-"
                resultado['kilometrajeAuto'] = form.cleaned_data['kilometrajeAuto'] if form.cleaned_data['kilometrajeAuto'] is not None else 0
                resultado['observaciones'] = form.cleaned_data['observaciones'] if form.cleaned_data['observaciones'] is not None else "-"

                #Datos del deudor
                resultado['tiempoServicio'] = form.cleaned_data['tiempoServicio'] if form.cleaned_data['tiempoServicio'] is not None else "-"
                resultado['ingresos'] = form.cleaned_data['ingresos'] if form.cleaned_data['ingresos'] is not None else "-"
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
                request.session['resultado'] = resultado
              
            except Exception as e:
                logger.error("Error in fideicomiso_view: %s", e)
                messages.error(request, 'An error occurred while processing your request.')
        else:
            logger.warning("Form is not valid: %s", form.errors)
    else:
        form = FideicomisoForm()
    
    return render(request, 'fideicomiso_form.html', {'form': form, 'resultado': resultado})
    