from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Modulo, Quiz, ResultadoQuiz, Opcion
from .forms import QuizRespuestaForm

@login_required
def quiz_modulo(request, curso_id, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id, curso_id=curso_id)
    quiz = get_object_or_404(Quiz, modulo=modulo)
    preguntas = quiz.preguntas.all()
    
    resultado = ResultadoQuiz.objects.filter(
        usuario=request.user,
        quiz=quiz
    ).order_by('-fecha_realizacion').first()

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
            ResultadoQuiz.objects.create(
                usuario=request.user,
                quiz=quiz,
                puntaje=puntaje,
                aprobado=aprobado
            )
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
