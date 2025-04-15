import openpyxl
from django.http import JsonResponse, HttpResponse
from .models import Cliente, Boleto, Tombola
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