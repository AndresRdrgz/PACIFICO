from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Curso, Modulo, Tema, ProgresoCurso, ProgresoTema, Feedback, ResultadoQuiz, Quiz
from .forms import FeedbackForm

@login_required
def lista_cursos(request):
    estado = request.GET.get('estado', 'todos')
    usuario = request.user

    cursos_directos = Curso.objects.filter(usuarios_asignados=usuario)
    grupos = usuario.grupos_asignados.all()  # ✅ Correcto

    cursos_grupo = Curso.objects.filter(grupos_asignados__in=grupos)

    cursos = (cursos_directos | cursos_grupo).distinct()

    if not usuario.is_superuser:
        cursos = cursos.filter(Q(usuarios_asignados=usuario) | Q(grupos_asignados__usuarios_asignados=usuario))

    if estado == "no-iniciados":
        cursos = cursos.exclude(progresocurso__usuario=usuario)
    elif estado == "en-progreso":
        cursos = cursos.filter(progresocurso__usuario=usuario, progresocurso__completado=False)
    elif estado == "completados":
        cursos = cursos.filter(progresocurso__usuario=usuario, progresocurso__completado=True)

    # Calcular el progreso de cada curso para todas las pestañas
    cursos_con_progreso = []
    for curso in cursos:
        progreso, _ = ProgresoCurso.objects.get_or_create(usuario=usuario, curso=curso)
        
        # Calcular progreso igual que en detalle_curso
        temas_completados_count = ProgresoTema.objects.filter(
            usuario=usuario,
            tema__modulo__curso=curso,
            completado=True
        ).count()

        quizzes_aprobados_count = ResultadoQuiz.objects.filter(
            usuario=usuario,
            quiz__modulo__curso=curso,
            aprobado=True
        ).count()
        
        total_temas = sum(mod.temas.count() for mod in curso.modulos.all())
        total_quizzes = Quiz.objects.filter(modulo__curso=curso).count()
        encuesta_completada = progreso.encuesta_completada
        
        total_elementos = total_temas + total_quizzes + 1  # Se suma 1 por la encuesta
        total_completados = temas_completados_count + quizzes_aprobados_count + (1 if encuesta_completada else 0)

        progreso_percent = round((total_completados / total_elementos) * 100) if total_elementos > 0 else 0
        progreso_percent = min(progreso_percent, 100)
        
        # Agregar el progreso al curso como atributo
        curso.progreso_percent = progreso_percent
        cursos_con_progreso.append(curso)
    
    cursos = cursos_con_progreso

    return render(request, 'capacitaciones_app/cursos.html', {'cursos': cursos, 'estado': estado})


@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    usuario = request.user

    progreso, _ = ProgresoCurso.objects.get_or_create(usuario=usuario, curso=curso)

    temas_completados_ids = ProgresoTema.objects.filter(
        usuario=usuario,
        tema__modulo__curso=curso,
        completado=True
    ).values_list('tema_id', flat=True)

    quizzes_aprobados_count = ResultadoQuiz.objects.filter(
        usuario=usuario,
        quiz__modulo__curso=curso,
        aprobado=True
    ).count()
    
    total_temas = sum(mod.temas.count() for mod in curso.modulos.all())
    total_quizzes = Quiz.objects.filter(modulo__curso=curso).count()
    encuesta_completada = progreso.encuesta_completada  # Nuevo campo para verificar si la encuesta está completada
    
    total_elementos = total_temas + total_quizzes + 1  # Se suma 1 por la encuesta
    total_completados = len(temas_completados_ids) + quizzes_aprobados_count + (1 if encuesta_completada else 0)

    progreso_percent = round((total_completados / total_elementos) * 100) if total_elementos > 0 else 0
    progreso_percent = min(progreso_percent, 100)

    curso_completado = (progreso_percent == 100) and encuesta_completada    # Verificar diferentes tipos de notificaciones
    mostrar_notificacion_encuesta = request.GET.get('encuesta_ya_completada') == 'true'
    mostrar_notificacion_quiz = request.GET.get('quiz_completado_exitoso') == 'true'
    mostrar_notificacion_certificado = request.GET.get('certificado_ya_descargado') == 'true'
    puntaje_quiz = request.GET.get('puntaje', '')

    return render(request, 'capacitaciones_app/detalle_curso.html', {
        'curso': curso,
        'progreso': progreso,
        'total_modulos': curso.modulos.count(),
        'progreso_percent': progreso_percent,
        'temas_completados_ids': temas_completados_ids,
        'curso_completado': curso_completado, 
        'cert_warning': False,
        'mostrar_notificacion_encuesta': mostrar_notificacion_encuesta,
        'mostrar_notificacion_quiz': mostrar_notificacion_quiz,
        'mostrar_notificacion_certificado': mostrar_notificacion_certificado,
        'puntaje_quiz': puntaje_quiz,
    })



@login_required
def ver_tema(request, curso_id, tema_id):
    curso = get_object_or_404(Curso, id=curso_id)
    tema = get_object_or_404(Tema, id=tema_id)
    completado = ProgresoTema.objects.filter(usuario=request.user, tema=tema, completado=True).exists()
    archivos = tema.archivos.all()
    instancia_feedback = Feedback.objects.filter(usuario=request.user, tema=tema).first()

    if request.method == 'POST':
        # Verificar si ya envió feedback para este tema
        if instancia_feedback:
            # Redirigir con parámetro para mostrar notificación
            url = reverse('ver_tema', kwargs={'curso_id': curso.id, 'tema_id': tema.id})
            return HttpResponseRedirect(f'{url}?feedback_ya_enviado=true')
            
        form = FeedbackForm(request.POST, instance=instancia_feedback)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.usuario = request.user
            fb.tema = tema
            fb.save()
            # Redirigir con parámetro para mostrar notificación de éxito
            url = reverse('ver_tema', kwargs={'curso_id': curso.id, 'tema_id': tema.id})
            return HttpResponseRedirect(f'{url}?feedback_enviado_exitoso=true')
    else:
        form = FeedbackForm(instance=instancia_feedback)

    feedbacks = tema.feedbacks.select_related('usuario')[:5]
    
    # Verificar notificaciones de feedback
    mostrar_notificacion_feedback_ya_enviado = request.GET.get('feedback_ya_enviado') == 'true'
    mostrar_notificacion_feedback_exitoso = request.GET.get('feedback_enviado_exitoso') == 'true'
    
    return render(request, 'capacitaciones_app/ver_tema.html', {
        'curso': curso,
        'tema': tema,
        'completado': completado,
        'archivos': archivos,
        'form': form,
        'feedbacks': feedbacks,
        'mostrar_notificacion_feedback_ya_enviado': mostrar_notificacion_feedback_ya_enviado,
        'mostrar_notificacion_feedback_exitoso': mostrar_notificacion_feedback_exitoso,
    })


@login_required
def marcar_tema_completado(request, tema_id):
    tema = get_object_or_404(Tema, id=tema_id)
    # Ya no se requiere feedback para marcar como completado
    progreso, _ = ProgresoTema.objects.get_or_create(usuario=request.user, tema=tema)
    progreso.completado = True
    progreso.fecha_completado = timezone.now()
    progreso.save()

    total_temas = tema.modulo.temas.count()
    temas_completados = ProgresoTema.objects.filter(usuario=request.user, tema__modulo=tema.modulo, completado=True).count()

    if temas_completados == total_temas:
        pc, _ = ProgresoCurso.objects.get_or_create(usuario=request.user, curso=tema.modulo.curso)
        pc.modulos_completados.add(tema.modulo)
        if pc.modulos_completados.count() == tema.modulo.curso.modulos.count():
            pc.completado = True
            pc.fecha_completado = timezone.now()
        pc.save()

    return redirect('ver_tema', curso_id=tema.modulo.curso.id, tema_id=tema.id)
