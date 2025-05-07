from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from PyPDF2 import PdfReader, PdfWriter

from .models import (
    Curso, Modulo, Tema, ProgresoCurso, ProgresoTema,
    ArchivoAdicional, Quiz, Pregunta, Opcion, ResultadoQuiz,
    Feedback, 
)
from .forms import QuizRespuestaForm, FeedbackForm


@login_required
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'capacitaciones_app/cursos.html', {
        'cursos': cursos,
    })


@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    progreso, _ = ProgresoCurso.objects.get_or_create(
    usuario=request.user,
    curso=curso
)


    temas_completados_ids = ProgresoTema.objects.filter(
        usuario=request.user,
        tema__modulo__curso=curso,
        completado=True
    ).values_list('tema_id', flat=True)

    quizzes_aprobados_count = ResultadoQuiz.objects.filter(
        usuario=request.user,
        quiz__modulo__curso=curso,
        aprobado=True
    ).count()

    total_temas = sum(
        m.temas.count() for m in curso.modulos.all()
    )
    total_quizzes = Quiz.objects.filter(
        modulo__curso=curso
    ).count()
    total_elementos = total_temas + total_quizzes
    total_completados = len(temas_completados_ids) + quizzes_aprobados_count

    progreso_percent = round((total_completados / total_elementos) * 100) \
        if total_elementos > 0 else 0
    progreso_percent = min(progreso_percent, 100)

    return render(request, 'capacitaciones_app/detalle_curso.html', {
        'curso': curso,
        'progreso': progreso,
        'total_modulos': curso.modulos.count(),
        'progreso_percent': progreso_percent,
        'temas_completados_ids': temas_completados_ids,
    })


@login_required
def ver_tema(request, curso_id, tema_id):
    curso = get_object_or_404(Curso, id=curso_id)
    tema  = get_object_or_404(Tema, id=tema_id)

    completado = ProgresoTema.objects.filter(
        usuario=request.user,
        tema=tema,
        completado=True
    ).exists()
    archivos = tema.archivos.all()

    # — Feedback: sólo obtenemos el feedback existente, no creamos en GET —
    instancia_feedback = Feedback.objects.filter(
        usuario=request.user,
        tema=tema
    ).first()

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=instancia_feedback)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.usuario = request.user
            fb.tema    = tema
            fb.save()
            messages.success(request, "¡Gracias por tu feedback!")
            return redirect('ver_tema', curso_id=curso.id, tema_id=tema.id)
    else:
        form = FeedbackForm(instance=instancia_feedback)

    feedbacks = tema.feedbacks.select_related('usuario')[:5]
    # ——————————————————————————————————————————————

    return render(request, 'capacitaciones_app/ver_tema.html', {
        'curso': curso,
        'tema': tema,
        'completado': completado,
        'archivos': archivos,
        'form': form,
        'feedbacks': feedbacks,
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from .models import Tema, ProgresoTema, ProgresoCurso, Feedback

@login_required
def marcar_tema_completado(request, tema_id):
    tema = get_object_or_404(Tema, id=tema_id)

    # ——— Validación de feedback obligatorio ———
    try:
        fb = Feedback.objects.get(usuario=request.user, tema=tema)
        # Si no tiene puntuación, consideramos que no ha completado la encuesta
        if fb.puntuacion is None:
            raise Feedback.DoesNotExist
    except Feedback.DoesNotExist:
        messages.error(
            request,
            "Por favor completa la encuesta de satisfacción antes de marcar el tema como completado."
        )
        return redirect('ver_tema', curso_id=tema.modulo.curso.id, tema_id=tema.id)
    # ————————————————————————————————

    # Marcar el tema como completado
    progreso, _ = ProgresoTema.objects.get_or_create(
        usuario=request.user,
        tema=tema
    )
    progreso.completado = True
    progreso.fecha_completado = timezone.now()
    progreso.save()

    # Si este cierre completa el módulo, actualizar progreso de curso
    total_temas = tema.modulo.temas.count()
    temas_completados = ProgresoTema.objects.filter(
        usuario=request.user,
        tema__modulo=tema.modulo,
        completado=True
    ).count()

    if temas_completados == total_temas:
        pc, _ = ProgresoCurso.objects.get_or_create(
            usuario=request.user,
            curso=tema.modulo.curso
        )
        pc.modulos_completados.add(tema.modulo)
        # Si completa todos los módulos, cerrar curso
        if pc.modulos_completados.count() == tema.modulo.curso.modulos.count():
            pc.completado = True
            pc.fecha_completado = timezone.now()
        pc.save()

    return redirect(
        'ver_tema',
        curso_id=tema.modulo.curso.id,
        tema_id=tema.id
    )


@login_required
def quiz_modulo(request, curso_id, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id, curso_id=curso_id)
    quiz = get_object_or_404(Quiz, modulo=modulo)
    preguntas = quiz.preguntas.all()
    resultado = ResultadoQuiz.objects.filter(
        usuario=request.user,
        quiz=quiz
    ).order_by('-fecha_realizacion').first()

    permitir_reintento = (
        resultado is None or request.GET.get('reintentar') == '1'
    )
    if request.method == 'POST' and permitir_reintento:
        form = QuizRespuestaForm(request.POST, preguntas=preguntas)
        if form.is_valid():
            puntaje = 0
            for pregunta in preguntas:
                resp_id = int(
                    form.cleaned_data.get(f"pregunta_{pregunta.id}", 0)
                )
                opcion = Opcion.objects.get(id=resp_id)
                if opcion.es_correcta:
                    puntaje += pregunta.puntaje
            aprobado = puntaje >= 81
            ResultadoQuiz.objects.create(
                usuario=request.user,
                quiz=quiz,
                puntaje=puntaje,
                aprobado=aprobado
            )
            messages.success(
                request,
                f"Tu puntaje es: {puntaje}/100"
            )
            return redirect(f"{request.path}?reintentar=0")
    else:
        form = QuizRespuestaForm(preguntas=preguntas)

    return render(request, 'capacitaciones_app/quiz_modulo.html', {
        'curso': modulo.curso,
        'modulo': modulo,
        'quiz': quiz,
        'form': form,
        'resultado': resultado,
        'permitir_reintento': permitir_reintento,
    })


@login_required
def certificado(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    total_temas = sum(
        m.temas.count() for m in curso.modulos.all()
    )
    temas_completados = ProgresoTema.objects.filter(
        usuario=request.user,
        tema__modulo__curso=curso,
        completado=True
    ).count()

    if temas_completados < total_temas:
        messages.error(
            request,
            "Aún no has completado todos los temas del curso."
        )
        return redirect('detalle_curso', curso_id=curso.id)

    nombre = (request.user.get_full_name() or request.user.username).title()
    fecha = timezone.now().strftime('%d/%m/%Y')
    plantilla_path = (
        settings.BASE_DIR / 'capacitaciones_app' /
        'static' / 'capacitaciones_app' / 'plantilla.pdf'
    )

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(letter))
    pagina_ancho = 792
    font_name = "Helvetica-Oblique"
    tamaño_inicial = 40
    tamaño_minimo = 20

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

    response = HttpResponse(
        output.read(),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="certificado_{nombre}.pdf"'
    )
    return response
