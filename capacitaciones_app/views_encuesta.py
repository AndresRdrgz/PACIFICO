from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Curso

@login_required
def encuesta_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        # Aquí puedes guardar las respuestas si lo deseas
        # calidad = request.POST.get('calidad')
        # utilidad = request.POST.get('utilidad')
        # comentarios = request.POST.get('comentarios')
        return render(request, 'capacitaciones_app/encuesta_curso.html', {'curso': curso, 'enviado': True})
    return render(request, 'capacitaciones_app/encuesta_curso.html', {'curso': curso})
