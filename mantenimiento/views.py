import openpyxl
from django.shortcuts import render
from django.contrib import messages
from .models import Patrono

def cargaPatronos(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file.name.endswith(".xlsx"):
            messages.error(request, "Please upload a valid .xlsx file.")
            return render(request, "mantenimiento/cargaPatronos.html")

        error_rows = []
        try:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            for idx, row in enumerate(sheet.iter_rows(min_row=1, values_only=True), start=1):
                try:
                    codigo, descripcion, agrupador, selectDescuento, porServDesc, montoFijo, disketCentral = row
                    Patrono.objects.update_or_create(
                        codigo=codigo,
                        defaults={
                            "descripcion": descripcion,
                            "agrupador": agrupador,
                            "selectDescuento": selectDescuento,
                            "porServDesc": porServDesc if porServDesc else None,
                            "montoFijo": montoFijo if montoFijo else None,
                            "disketCentral": disketCentral,
                        },
                    )
                except Exception as e:
                    error_rows.append((idx, str(e)))

            if error_rows:
                error_summary = "\n".join([f"Row {row}: {error}" for row, error in error_rows])
                messages.warning(request, f"Some rows were skipped due to errors:\n{error_summary}")
            else:
                messages.success(request, "Patrono list uploaded successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    patronos = Patrono.objects.all()
    return render(request, "mantenimiento/cargaPatronos.html", {"patronos": patronos})