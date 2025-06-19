from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EncuestaSatisfaccionCursoForm
from django.contrib.auth.decorators import login_required

@login_required
def encuesta_satisfaccion_curso(request):
    if request.method == 'POST':
        form = EncuestaSatisfaccionCursoForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.usuario = request.user
            encuesta.save()
            messages.success(request, '¡Gracias por responder la encuesta!')
            return redirect('encuesta_satisfaccion_curso')
    else:
        form = EncuestaSatisfaccionCursoForm()
    return render(request, 'capacitaciones_app/encuesta_curso.html', {'form': form})
