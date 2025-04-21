import openpyxl
from django.http import JsonResponse, HttpResponse
from .models import Cliente, Boleto, Tombola, FormularioTombola
from django.shortcuts import redirect, render
from django.contrib import messages

def fetch_boletos_by_cedula(request):
    cedula = request.GET.get('cedula')  # Get the cedula from the request
    try:
        cliente = Cliente.objects.get(cedulaCliente=cedula)  # Find the cliente by cedula
        boletos = Boleto.objects.filter(cliente=cliente)  # Get boletos related to the cliente
        boletos_data = [
            {
                'id': boleto.id,
                'fecha_creacion': boleto.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                'tombola': boleto.tombola.id,
                'canalOrigen': boleto.canalOrigen,
            }
            for boleto in boletos
        ]
        return JsonResponse({'success': True, 'boletos': boletos_data})
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente no encontrado.'})
    
def descargar_plantilla(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Plantilla Clientes"

    # Add headers to the sheet
    headers = ["Cedula", "Nombre completo", "Cantidad boletos"]
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Set the response to serve the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_clientes.xlsx'

    # Save the workbook to the response
    workbook.save(response)
    return response


def carga_masiva(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'success': False, 'message': 'Por favor, suba un archivo válido.'})

        try:
            # Load the uploaded Excel file
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            # Iterate through each row in the sheet (skipping the header row)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                cedula, nombre_completo, cantidad_boletos = row

                # Validate the data
                if not cedula or not nombre_completo or not cantidad_boletos:
                    continue  # Skip rows with missing data

                # Check if the cliente exists
                cliente, created = Cliente.objects.get_or_create(
                    cedulaCliente=cedula,
                    defaults={'nombreCliente': nombre_completo}
                )
                if created:
                    print(f"Cliente creado exitosamente: {cliente.nombreCliente}")
                else:
                    print(f"Cliente ya existe: {cliente.nombreCliente}")

                # Create the specified number of boletos for the cliente
                for _ in range(int(cantidad_boletos)):
                    Boleto.objects.create(
                        cliente=cliente,
                        tombola=Tombola.objects.first(),  # Replace with the appropriate tombola instance
                        canalOrigen='Carga masiva'
                    )

            return JsonResponse({'success': True, 'message': 'Carga masiva completada exitosamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ocurrió un error al procesar el archivo: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

def download_formularios_excel(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Formularios"

    # Add headers to the sheet
    headers = ["Nombre", "Apellido", "Celular", "Correo Electrónico", "Oficial", "Tómbola", "Fecha de Creación"]
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Add data to the sheet
    formularios = FormularioTombola.objects.all()
    for row_num, formulario in enumerate(formularios, start=2):
        sheet.cell(row=row_num, column=1, value=formulario.nombre)
        sheet.cell(row=row_num, column=2, value=formulario.apellido)
        sheet.cell(row=row_num, column=3, value=formulario.celular)
        sheet.cell(row=row_num, column=4, value=formulario.correo_electronico)
        sheet.cell(row=row_num, column=5, value=formulario.oficial)
        # Convert the Tombola object to a string (e.g., its name or ID)
        sheet.cell(row=row_num, column=6, value=str(formulario.tombola))
        sheet.cell(row=row_num, column=7, value=formulario.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'))

    # Set the response to serve the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=formularios.xlsx'
    workbook.save(response)
    return response

def download_boletos_excel(request):
    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Boletos"

    # Add headers to the sheet
    headers = ["ID", "Cliente", "Tómbola", "Fecha de Creación"]
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Add data to the sheet
    boletos = Boleto.objects.all()  # Replace with your actual model name
    for row_num, boleto in enumerate(boletos, start=2):
        sheet.cell(row=row_num, column=1, value=boleto.id)
        sheet.cell(row=row_num, column=2, value=str(boleto.cliente))
        sheet.cell(row=row_num, column=3, value=str(boleto.tombola))
        sheet.cell(row=row_num, column=4, value=boleto.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'))

    # Set the response to serve the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=boletos.xlsx'
    workbook.save(response)
    return response

def listar_boletos(request):
    """
    API endpoint to retrieve a list of all boletos in JSON format.
    """
    boletos = Boleto.objects.all()
    boletos_data = [
        {
            'id': boleto.id,
            'cliente': str(boleto.cliente),
            'tombola': str(boleto.tombola),
            'fecha_creacion': boleto.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'canal_origen': boleto.canalOrigen,
        }
        for boleto in boletos
    ]
    return JsonResponse({'success': True, 'boletos': boletos_data})

def listar_formularios(request):
    formularios = FormularioTombola.objects.all()
    formularios_data = [
            {
                'id': formulario.id,
                'nombre': formulario.nombre,
                'apellido': formulario.apellido,
                'celular': formulario.celular,
                'correo_electronico': formulario.correo_electronico,
                'oficial': formulario.oficial,
                'tombola': str(formulario.tombola),
                'fecha_creacion': formulario.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for formulario in formularios
    ]
    return JsonResponse({'success': True, 'formularios': formularios_data})
