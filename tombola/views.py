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

import os
import smtplib

import os


# Create your views here.
def moduloTombola(request):
    tombola_list = FormularioTombola.objects.all()
    boleto_list = Boleto.objects.all()  # Assuming you have a model named Boleto
    return render(request, 'moduloTombola.html', {'tombola_list': tombola_list, 'boleto_list': boleto_list})

def formularioTombola(request):
    try:
        if request.method == 'POST':
            form = FormularioTombolaForm(request.POST)
            if form.is_valid():
                print("Formulario válido")
                formulario = form.save()  # Save the FormularioTombola instance
                
                # Check if Cliente with given cedula exists, otherwise create it
                cedulaCliente = form.cleaned_data.get('cedulaCliente')  # Assuming the form has a 'cedula' field
                nombre = form.cleaned_data.get('nombre')  # Assuming the form has a 'nombre' field
                apellido = form.cleaned_data.get('apellido')  # Assuming the form has an 'apellido' field
                edad = form.cleaned_data.get('edad')  # Assuming the form has an 'edad' field
                sexo = form.cleaned_data.get('sexo')  # Assuming the form has a 'sexo' field
                
                cliente, created = Cliente.objects.get_or_create(
                    cedulaCliente=cedulaCliente,
                    defaults={
                        'nombreCliente': f"{nombre} {apellido}",
                        'edad': edad,
                        'sexo': sexo
                    }
                )

                # Check if a Boleto already exists for this tombola, cedula, and origin
                existing_boleto = Boleto.objects.filter(
                    tombola=formulario.tombola,
                    cliente=cliente,
                    canalOrigen='Formulario'
                ).first()
                print(f"Existing Boleto: {existing_boleto}")
                if existing_boleto:
                    print("Cliente ya está participando")
                    return render(request, 'confirmacion.html', {
                        'error_message': "Cliente ya está participando",
                    })

                # Create the Boleto instance
                boleto = Boleto.objects.create(
                    tombola=formulario.tombola,  # Assuming FormularioTombola has a tombola ForeignKey
                    cliente=cliente,  # Associate the Boleto with the Cliente
                    canalOrigen='Formulario'  # Set the canalOrigen field
                )

                return redirect('confirmacion', boleto_id=boleto.id)  # Redirect to confirmation page with boleto_id
        else:
            form = FormularioTombolaForm()
        
        return render(request, 'formularioTombola.html', {'form': form})
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'formularioTombola.html', {
            'form': FormularioTombolaForm(),
            'error_message': "Ocurrió un error al procesar el formulario. Por favor, inténtelo de nuevo."
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

    # Set font and position for the boleto ID
    c.setFont("Helvetica-Bold", 20)
    boleto_text = f"Boleto ID: {boleto_id}"
    boleto_text_width = c.stringWidth(boleto_text, "Helvetica-Bold", 20)
    c.drawString((page_width - boleto_text_width) / 2, page_height / 2, boleto_text)

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
        cc_emails = ["arodriguez@fpacifico.com", "snunez@fpacifico.com"]  # CC recipients

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