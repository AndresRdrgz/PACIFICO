import openpyxl
from django.http import HttpResponse, FileResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from .forms import FormularioTombolaForm
from .models import FormularioTombola, Boleto
from pacifico.models import Cliente
from io import BytesIO
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from django.conf import settings
from django.core.mail import EmailMessage
from .models import FormularioTombola, Boleto, CargaMasiva


import os
import smtplib

import os


from django.shortcuts import render, redirect
from .models import CargaMasiva, Boleto, FormularioTombola
from pacifico.models import Cliente
from .forms import FormularioTombolaForm

def moduloTombola(request):
    # Traer boletos para la tabla de Participantes
    boletos = Boleto.objects.select_related('formulario_origen', 'tombola', 'cliente')
    boleto_data = []

    for b in boletos:
        f = getattr(b, 'formulario_origen', None)

        if f:  # Si proviene de formulario
            nombre = f.nombre
            apellido = f.apellido
            celular = f.celular
            correo = f.correo_electronico
            oficial = f.oficial
            fecha = f.fecha_creacion
        else:  # Si proviene de carga masiva
            if b.cliente and b.cliente.nombreCliente:
                partes = b.cliente.nombreCliente.split()
                nombre = partes[0]
                apellido = partes[-1] if len(partes) > 1 else ""
            else:
                nombre = "Desconocido"
                apellido = ""
            celular = ""
            correo = ""
            oficial = ""
            fecha = b.fecha_creacion

        boleto_data.append({
            "nombre": nombre,
            "apellido": apellido,
            "celular": celular,
            "correo": correo,
            "oficial": oficial,
            "canal": b.canalOrigen,
            "tombola": b.tombola.nombre if b.tombola else "-",
            "boleto_id": b.id,
            "fecha": fecha,
        })

    # Historial de cargas masivas
    cargas = CargaMasiva.objects.order_by('-fecha_subida')

    return render(request, 'moduloTombola.html', {
        'boleto_data': boleto_data,
        'cargas_masivas': cargas,
    })


def formularioTombola(request):
    try:
        if request.method == 'POST':
            form = FormularioTombolaForm(request.POST)
            if form.is_valid():
                formulario = form.save(commit=False)

                # Datos del cliente
                cedulaCliente = form.cleaned_data.get('cedulaCliente')
                nombre = form.cleaned_data.get('nombre')
                apellido = form.cleaned_data.get('apellido')
                edad = form.cleaned_data.get('edad')
                sexo = form.cleaned_data.get('sexo')

                cliente, created = Cliente.objects.get_or_create(
                    cedulaCliente=cedulaCliente,
                    defaults={
                        'nombreCliente': f"{nombre} {apellido}",
                        'edad': edad,
                        'sexo': sexo
                    }
                )

                # Guardar formulario para poder asignar boleto después
                formulario.save()

                # Validar si ya existe un boleto desde formulario
                existente = Boleto.objects.filter(
                    tombola=formulario.tombola,
                    cliente=cliente,
                    canalOrigen='Formulario'
                ).first()

                if existente:
                    return render(request, 'confirmacion.html', {
                        'error_message': "Cliente ya está participando"
                    })

                # Crear boleto
                boleto = Boleto.objects.create(
                    tombola=formulario.tombola,
                    cliente=cliente,
                    canalOrigen='Formulario'
                )

                # 🔥 ESTA ES LA PARTE CLAVE
                formulario.boleto_asociado = boleto
                formulario.save()

                # Enviar por correo
                enviar_boleto_por_correo(boleto, formulario)

                return redirect('confirmacion', boleto_id=boleto.id)
        else:
            form = FormularioTombolaForm()
        
        return render(request, 'formularioTombola.html', {'form': form})
    
    except Exception as e:
        print(f"Error: {e}")
        return render(request, 'formularioTombola.html', {
            'form': FormularioTombolaForm(),
            'error_message': "Ocurrió un error al procesar el formulario."
        })


def confirmacion(request, boleto_id):
    return render(request, 'confirmacion.html', {'boleto_id': boleto_id})

def validadorCedula(request):
    return render(request, 'validadorCedula.html')


#GENERAR BOLETO EN FORMATO PDF
def generate_boleto_pdf(template_path, output_path, boleto_id):
    """
    Generate a boleto PDF by overlaying the boleto ID onto a PDF template.

    :param template_path: Path to the PDF template
    :param output_path: Path to save the generated boleto
    :param boleto_id: ID of the boleto
    """
    # Create a BytesIO buffer to hold the overlay
    buffer = BytesIO()
    # Read the template PDF to get its page size
    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]
    page_width = float(template_page.mediabox.width)
    page_height = float(template_page.mediabox.height)

    # Create a canvas with the same size as the template
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    # Set font, color, and position for the boleto ID
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(1, 0, 0)  # Set the font color to red (RGB: 1, 0, 0)
    boleto_text = f"Boleto No. {boleto_id:06d}"  # Format the ID as a 6-digit number with leading zeros
    boleto_text_width = c.stringWidth(boleto_text, "Helvetica-Bold", 30)
    c.drawString((page_width - boleto_text_width) / 2+43, page_height * 0.605, boleto_text)

    # Finalize the overlay
    c.save()

    # Move the buffer to the beginning
    buffer.seek(0)

    # Read the template PDF
    overlay_pdf = PdfReader(buffer)

    # Create a new PDF writer
    writer = PdfWriter()

    # Merge the overlay onto the template
    for page in template_pdf.pages:
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    # Write the final PDF to the output path
    with open(output_path, "wb") as output_file:
        writer.write(output_file)



def download_boleto(request, boleto_id):
    """
    Generate and download a boleto PDF with the given boleto ID.
    """
    # Define paths
    template_path = os.path.join(settings.BASE_DIR, "tombola/templates/boleto_template.pdf")
    output_path = os.path.join(settings.BASE_DIR, f"tombola/temp/boleto_{boleto_id}.pdf")

    # Check if the template exists
    if not os.path.exists(template_path):
        print(f"Template not found at {template_path}")
        raise Http404("PDF template not found.")

    # Generate the boleto PDF
    generate_boleto_pdf(template_path, output_path, boleto_id)

    # Serve the file as a response
    response = FileResponse(open(output_path, "rb"), as_attachment=True, filename=f"boleto_{boleto_id}.pdf")

    # ✅ En local, no intentes borrar de inmediato para evitar PermissionError
    if not settings.DEBUG:
        try:
            os.remove(output_path)
        except Exception as e:
            print(f"No se pudo eliminar el archivo temporal: {e}")

    return response

    # Optionally delete the file after serving
    os.remove(output_path)

    return response





def send_boleto_email(request, boleto_id):
    """
    Generate the boleto PDF and send it via email.
    """
    try:
        # Get the Boleto instance
        boleto = Boleto.objects.get(id=boleto_id)

        # Get the related FormularioTombola instance
        formulario = FormularioTombola.objects.filter(tombola=boleto.tombola, cedulaCliente=boleto.cliente.cedulaCliente).first()

        if not formulario or not formulario.correo_electronico:
            return render(request, 'confirmacion.html', {
                'error_message': "No se encontró un correo electrónico asociado al formulario.",
                'boleto_id': boleto_id
            })

        # Define paths
        template_path = os.path.join(settings.BASE_DIR, "tombola/templates/boleto_template.pdf")
        output_path = os.path.join(settings.BASE_DIR, f"tombola/temp/boleto_{boleto_id}.pdf")

        # Check if the template exists
        if not os.path.exists(template_path):
            raise Http404("PDF template not found.")

        # Generate the boleto PDF
        generate_boleto_pdf(template_path, output_path, boleto_id)

        # Recipient email from the formulario
        recipient_email = formulario.correo_electronico
        cc_emails = ["arodriguez@fpacifico.com", "jacastillo@fpacifico.com"]  # CC recipients

        # Email subject and body
        subject = "Tu boleto de participación"
        body = f"Hola {formulario.nombre} {formulario.apellido},\n\nAdjunto encontrarás tu boleto de participación con el ID: {boleto_id}.\n\nSaludos,\nEquipo de FPACIFICO"

        # Create the email using Django's EmailMessage
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="tombola@fpacifico.com",
            to=[recipient_email],
            cc=cc_emails,
        )
        email.attach_file(output_path)

        # Send the email
        email.send()

        # Optionally delete the generated PDF after sending
        os.remove(output_path)

        # Render the same template with a success message
        return render(request, 'confirmacion.html', {
            'success_message': "El boleto ha sido enviado correctamente a tu correo.",
            'boleto_id': boleto_id
        })

    except Boleto.DoesNotExist:
        return render(request, 'confirmacion.html', {
            'error_message': "No se encontró el boleto especificado.",
            'boleto_id': boleto_id
        })
    except Exception as e:
        return render(request, 'confirmacion.html', {
            'error_message': f"Error al enviar el correo: {str(e)}",
            'boleto_id': boleto_id
        })
    
    from django.core.mail import EmailMessage

def enviar_boleto_por_correo(boleto, formulario=None, correo=None, nombre=None, apellido=None):
    try:
        # Priorizar datos desde formulario si se proporciona
        if formulario:
            correo = formulario.correo_electronico
            nombre = formulario.nombre
            apellido = formulario.apellido

        if not correo:
            print("No se proporcionó un correo electrónico.")
            return

        # Generar PDF
        template_path = os.path.join(settings.BASE_DIR, "tombola/templates/boleto_template.pdf")
        output_path = os.path.join(settings.BASE_DIR, f"tombola/temp/boleto_{boleto.id}.pdf")

        generate_boleto_pdf(template_path, output_path, boleto.id)

        # Preparar correo
        cc_emails = ["arodriguez@fpacifico.com", "jacastillo@fpacifico.com"]
        subject = "Tu boleto de participación"
        body = f"Hola {nombre} {apellido},\n\nAdjunto encontrarás tu boleto de participación con el ID: {boleto.id:06d}.\n\nSaludos,\nEquipo de FPACIFICO"

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="tombola@fpacifico.com",
            to=[correo],
            cc=cc_emails,
        )

        with open(output_path, "rb") as pdf:
            email.attach(f"boleto_{boleto.id}.pdf", pdf.read(), "application/pdf")

        email.send()

        if not settings.DEBUG:
            os.remove(output_path)

        print(f"Correo enviado a {correo}")

    except Exception as e:
        print(f"Error al enviar el boleto por correo: {e}")

from .models import CargaMasiva
import openpyxl
from django.utils.timezone import localtime

def descargar_excel_cargas(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cargas Masivas"

    headers = ["ID", "Archivo", "Cantidad de Registros", "Usuario", "Fecha de Subida"]
    ws.append(headers)

    cargas = CargaMasiva.objects.all().order_by('-fecha_subida')

    for carga in cargas:
        ws.append([
            carga.id,
            carga.archivo,
            carga.cantidad_registros,
            carga.usuario,
            localtime(carga.fecha_subida).strftime("%Y-%m-%d %H:%M:%S")
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=cargas_masivas.xlsx'
    wb.save(response)
    return response
