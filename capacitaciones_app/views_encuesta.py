from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EncuestaSatisfaccionCursoForm
from .models import ProgresoCurso, Curso
from .models_encuesta import EncuestaSatisfaccionCurso

@login_required
def encuesta_satisfaccion_curso(request):
    curso_id = request.GET.get('curso_id') or request.POST.get('curso_id')

    if not curso_id:
        messages.error(request, 'Error: No se proporcionó un curso válido para la encuesta.')
        return redirect('lista_cursos')

    curso = get_object_or_404(Curso, id=curso_id)

    progreso = ProgresoCurso.objects.filter(usuario=request.user, curso=curso).first()
    if not progreso:
        messages.error(request, 'Error: No se encontró el progreso del curso. Por favor, contacte al administrador.')
        return redirect('detalle_curso', curso_id=curso.id)

    encuesta_existente = EncuestaSatisfaccionCurso.objects.filter(usuario=request.user, curso=curso).first()
    if encuesta_existente:
        messages.info(request, 'Ya has completado la encuesta para este curso.')
        return redirect('detalle_curso', curso_id=curso.id)

    if request.method == 'POST':
        form = EncuestaSatisfaccionCursoForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.usuario = request.user
            encuesta.curso = curso
            encuesta.save()

            progreso.encuesta_completada = True
            progreso.save()

            messages.success(request, '¡Gracias por responder la encuesta!')
            return redirect('detalle_curso', curso_id=curso.id)
        else:
            messages.error(request, 'Error: El formulario no es válido.')
    else:
        form = EncuestaSatisfaccionCursoForm()

    return render(request, 'capacitaciones_app/encuesta_curso.html', {
        'form': form,
        'curso': curso,
    })
