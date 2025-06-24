from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from PyPDF2 import PdfReader, PdfWriter
import io

from .models import Curso, ProgresoTema, ProgresoCurso

@login_required
def certificado(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)    # Verificar si ya descargó el certificado antes
    progreso_curso = ProgresoCurso.objects.filter(usuario=request.user, curso=curso).first()
    referer = request.META.get('HTTP_REFERER', '')
    
    # Solo mostrar notificación si NO viene de mi-progreso (permite re-descarga desde progreso)
    if progreso_curso and progreso_curso.certificado_descargado and 'mi-progreso' not in referer:
        # Redirigir a detalle del curso con notificación
        url = reverse('detalle_curso', kwargs={'curso_id': curso.id})
        return HttpResponseRedirect(f'{url}?certificado_ya_descargado=true')

    total_temas = sum(m.temas.count() for m in curso.modulos.all())
    temas_completados = ProgresoTema.objects.filter(
        usuario=request.user,
        tema__modulo__curso=curso,
        completado=True
    ).count()

    if temas_completados < total_temas:
        messages.error(request, "Aún no has completado todos los temas.")
        return redirect('detalle_curso', curso_id=curso.id)

    nombre = (request.user.get_full_name() or request.user.username).title()
    fecha = timezone.now().strftime('%d/%m/%Y')
    plantilla_path = settings.BASE_DIR / 'capacitaciones_app' / 'static' / 'capacitaciones_app' / 'plantilla.pdf'

    # Crear overlay del nombre y contenido
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(letter))

    pagina_ancho = 792
    tamaño_inicial = 40
    tamaño_minimo = 20
    font_name = "Helvetica-Oblique"

    c.setFont(font_name, tamaño_inicial)
    text_width = c.stringWidth(nombre, font_name, tamaño_inicial)

    while text_width > (pagina_ancho - 100) and tamaño_inicial > tamaño_minimo:
        tamaño_inicial -= 1
        c.setFont(font_name, tamaño_inicial)
        text_width = c.stringWidth(nombre, font_name, tamaño_inicial)

    x_nombre = (pagina_ancho - text_width) / 2
    c.drawString(x_nombre, 282, nombre)
    c.setFont("Helvetica", 16)
    c.drawString(186, 224, curso.titulo)
    c.setFont("Helvetica", 14)
    c.drawString(100, 60, f"Fecha: {fecha}")
    c.save()

    packet.seek(0)
    
    plantilla_pdf = PdfReader(str(plantilla_path))
    overlay_pdf = PdfReader(packet)
    writer = PdfWriter()
    
    page = plantilla_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    # Marcar certificado como descargado
    if progreso_curso:
        progreso_curso.certificado_descargado = True
        progreso_curso.fecha_descarga_certificado = timezone.now()
        progreso_curso.save()

    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{nombre}.pdf"'
    return response
