from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import json
import io
from django.db.models import Q, F, Count, Sum



from .models import (
    Curso, Modulo, Tema, ProgresoCurso, ProgresoTema,
    ArchivoAdicional, Quiz, Pregunta, Opcion, ResultadoQuiz,
    Feedback, GrupoAsignacion, Asignacion
)
from .forms import QuizRespuestaForm, FeedbackForm


@login_required
def lista_cursos(request):
    estado = request.GET.get('estado', 'todos')
    usuario = request.user

    cursos_directos = Curso.objects.filter(usuarios_asignados=usuario)
    grupos = GrupoAsignacion.objects.filter(usuarios_asignados=usuario)
    cursos_grupo = Curso.objects.filter(grupos_asignados__in=grupos)

    cursos = (cursos_directos | cursos_grupo).distinct()

    # 🔒 Si no es superuser, asegurar que solo vea los cursos asignados
    if not usuario.is_superuser:
        cursos = cursos.filter(Q(usuarios_asignados=usuario) | Q(grupos_asignados__usuarios_asignados=usuario))


    # Filtrar por estado
    if estado == "no-iniciados":
        cursos = cursos.exclude(progresocurso__usuario=usuario)
    elif estado == "en-progreso":
        cursos = cursos.filter(progresocurso__usuario=usuario, progresocurso__completado=False)
    elif estado == "completados":
        cursos = cursos.filter(progresocurso__usuario=usuario, progresocurso__completado=True)

    return render(request, 'capacitaciones_app/cursos.html', {
        'cursos': cursos,
        'estado': estado,
    })


@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    progreso, _ = ProgresoCurso.objects.get_or_create(usuario=request.user, curso=curso)

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

    total_temas = sum(m.temas.count() for m in curso.modulos.all())
    total_quizzes = Quiz.objects.filter(modulo__curso=curso).count()
    total_elementos = total_temas + total_quizzes
    total_completados = len(temas_completados_ids) + quizzes_aprobados_count

    progreso_percent = round((total_completados / total_elementos) * 100) if total_elementos > 0 else 0
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
    tema = get_object_or_404(Tema, id=tema_id)

    completado = ProgresoTema.objects.filter(usuario=request.user, tema=tema, completado=True).exists()
    archivos = tema.archivos.all()

    instancia_feedback = Feedback.objects.filter(usuario=request.user, tema=tema).first()

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=instancia_feedback)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.usuario = request.user
            fb.tema = tema
            fb.save()
            messages.success(request, "¡Gracias por tu feedback!")
            return redirect('ver_tema', curso_id=curso.id, tema_id=tema.id)
    else:
        form = FeedbackForm(instance=instancia_feedback)

    feedbacks = tema.feedbacks.select_related('usuario')[:5]

    return render(request, 'capacitaciones_app/ver_tema.html', {
        'curso': curso,
        'tema': tema,
        'completado': completado,
        'archivos': archivos,
        'form': form,
        'feedbacks': feedbacks,
    })


@login_required
def marcar_tema_completado(request, tema_id):
    tema = get_object_or_404(Tema, id=tema_id)

    try:
        fb = Feedback.objects.get(usuario=request.user, tema=tema)
        if fb.puntuacion is None:
            raise Feedback.DoesNotExist
    except Feedback.DoesNotExist:
        messages.error(request, "Por favor completa la encuesta antes de marcar como completado.")
        return redirect('ver_tema', curso_id=tema.modulo.curso.id, tema_id=tema.id)

    progreso, _ = ProgresoTema.objects.get_or_create(usuario=request.user, tema=tema)
    progreso.completado = True
    progreso.fecha_completado = timezone.now()
    progreso.save()

    total_temas = tema.modulo.temas.count()
    temas_completados = ProgresoTema.objects.filter(
        usuario=request.user, tema__modulo=tema.modulo, completado=True
    ).count()

    if temas_completados == total_temas:
        pc, _ = ProgresoCurso.objects.get_or_create(usuario=request.user, curso=tema.modulo.curso)
        pc.modulos_completados.add(tema.modulo)
        if pc.modulos_completados.count() == tema.modulo.curso.modulos.count():
            pc.completado = True
            pc.fecha_completado = timezone.now()
        pc.save()

    return redirect('ver_tema', curso_id=tema.modulo.curso.id, tema_id=tema.id)


@login_required
def quiz_modulo(request, curso_id, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id, curso_id=curso_id)
    quiz = get_object_or_404(Quiz, modulo=modulo)
    preguntas = quiz.preguntas.all()
    resultado = ResultadoQuiz.objects.filter(usuario=request.user, quiz=quiz).order_by('-fecha_realizacion').first()

    permitir_reintento = (resultado is None or request.GET.get('reintentar') == '1')

    if request.method == 'POST' and permitir_reintento:
        form = QuizRespuestaForm(request.POST, preguntas=preguntas)
        if form.is_valid():
            puntaje = 0
            for pregunta in preguntas:
                resp_id = form.cleaned_data.get(f"pregunta_{pregunta.id}")
                if resp_id:
                    opcion = Opcion.objects.get(id=resp_id)
                    if opcion.es_correcta:
                        puntaje += pregunta.puntaje

            aprobado = puntaje >= 81
            ResultadoQuiz.objects.create(usuario=request.user, quiz=quiz, puntaje=puntaje, aprobado=aprobado)
            messages.success(request, f"Tu puntaje es: {puntaje}/100")
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
    total_temas = sum(m.temas.count() for m in curso.modulos.all())
    temas_completados = ProgresoTema.objects.filter(usuario=request.user, tema__modulo__curso=curso, completado=True).count()

    if temas_completados < total_temas:
        messages.error(request, "Aún no has completado todos los temas.")
        return redirect('detalle_curso', curso_id=curso.id)

    nombre = (request.user.get_full_name() or request.user.username).title()
    fecha = timezone.now().strftime('%d/%m/%Y')
    plantilla_path = settings.BASE_DIR / 'capacitaciones_app' / 'static' / 'capacitaciones_app' / 'plantilla.pdf'

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

    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{nombre}.pdf"'
    return response


@user_passes_test(lambda u: u.is_staff)
def asignacion_admin(request):
    if request.method == 'POST':
        cursos_ids = request.POST.getlist('cursos')
        usuarios_ids = request.POST.getlist('usuarios')
        grupos_ids = request.POST.getlist('grupos')

        cursos = Curso.objects.filter(id__in=cursos_ids)
        usuarios = User.objects.filter(id__in=usuarios_ids)
        grupos = GrupoAsignacion.objects.filter(id__in=grupos_ids)

        for curso in cursos:
            for usuario in usuarios:
                if not curso.usuarios_asignados.filter(id=usuario.id).exists():
                    curso.usuarios_asignados.add(usuario)
                    Asignacion.objects.create(curso=curso, usuario=usuario, metodo='admin')

            for grupo in grupos:
                curso.grupos_asignados.add(grupo)
                for usuario in grupo.usuarios_asignados.all():
                    if not curso.usuarios_asignados.filter(id=usuario.id).exists():
                        curso.usuarios_asignados.add(usuario)
                        Asignacion.objects.create(curso=curso, usuario=usuario, grupo=grupo, metodo='admin')

        return redirect('asignacion_admin')

    cursos = Curso.objects.all()
    usuarios = User.objects.filter(is_active=True)
    grupos = GrupoAsignacion.objects.all()

    historial = []
    asignaciones = Asignacion.objects.select_related('curso', 'usuario', 'grupo').order_by('-fecha')

    for a in asignaciones:
        progreso = None
        completados = 0
        total_modulos = a.curso.modulos.count()
        fecha_final = None

        if a.usuario:
            progreso_obj = ProgresoCurso.objects.filter(usuario=a.usuario, curso=a.curso).first()
            if progreso_obj:
                completados = progreso_obj.modulos_completados.count()
                progreso = round((completados / total_modulos) * 100) if total_modulos > 0 else 0
                fecha_final = progreso_obj.fecha_completado

        historial.append({
            'asignacion': a,
            'progreso': progreso,
            'completados': completados,
            'total': total_modulos,
            'completado_en': fecha_final,
        })

    return render(request, 'capacitaciones_app/asignacion_admin.html', {
        'cursos': cursos,
        'usuarios': usuarios,
        'grupos': grupos,
        'historial': historial,
    })


@require_POST
@user_passes_test(lambda u: u.is_staff)
def asignar_curso_ajax(request):
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        usuario_id = data.get('usuario_id')
        grupo_id = data.get('grupo_id')

        curso = Curso.objects.get(id=curso_id)

        if usuario_id:
            usuario = User.objects.get(id=usuario_id)
            if not curso.usuarios_asignados.filter(id=usuario.id).exists():
                curso.usuarios_asignados.add(usuario)
                Asignacion.objects.create(curso=curso, usuario=usuario, metodo='dragdrop')
            mensaje = f'✅ Curso "{curso.titulo}" asignado a {usuario.username}.'
            return JsonResponse({'success': True, 'mensaje': mensaje})

        elif grupo_id:
            grupo = GrupoAsignacion.objects.get(id=grupo_id)
            curso.grupos_asignados.add(grupo)
            for usuario in grupo.usuarios_asignados.all():
                if not curso.usuarios_asignados.filter(id=usuario.id).exists():
                    curso.usuarios_asignados.add(usuario)
                    Asignacion.objects.create(curso=curso, usuario=usuario, grupo=grupo, metodo='dragdrop')
            mensaje = f'✅ Curso "{curso.titulo}" asignado al grupo "{grupo.nombre}".'
            return JsonResponse({'success': True, 'mensaje': mensaje})

        return JsonResponse({'success': False, 'mensaje': 'No se especificó usuario ni grupo.'})

    except Exception as e:
        return JsonResponse({'success': False, 'mensaje': str(e)})


@require_POST
@user_passes_test(lambda u: u.is_staff)
def desasignar_curso_ajax(request):
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        usuario_id = data.get('usuario_id')

        curso = Curso.objects.get(id=curso_id)
        user = User.objects.get(id=usuario_id)

        curso.usuarios_asignados.remove(user)
        return JsonResponse({'success': True, 'mensaje': 'Curso desasignado correctamente'})

    except Exception as e:
        return JsonResponse({'success': False, 'mensaje': str(e)})


def cursos_asignados_ajax(request, usuario_id):
    cursos = Curso.objects.filter(usuarios_asignados__id=usuario_id)
    data = list(cursos.values('id', 'titulo'))
    return JsonResponse({'cursos': data})


def exportar_asignaciones_excel(request):
    asignaciones = Asignacion.objects.select_related('curso', 'usuario', 'grupo').order_by('-fecha')

    data = []
    for a in asignaciones:
        data.append({
            'Fecha': a.fecha.strftime('%Y-%m-%d %H:%M'),
            'Curso': a.curso.titulo,
            'Usuario': a.usuario.username if a.usuario else '',
            'Grupo': a.grupo.nombre if a.grupo else '',
            'Método': a.metodo,
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="asignaciones.xlsx"'
    df.to_excel(response, index=False)
    return response
