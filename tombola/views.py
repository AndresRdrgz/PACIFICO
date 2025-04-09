from django.shortcuts import render, redirect
from .forms import FormularioTombolaForm

# Create your views here.
def moduloTombola(request):
    return render(request, 'moduloTombola.html')

def formularioTombola(request):
    if request.method == 'POST':
        form = FormularioTombolaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('moduloTombola')  # Replace 'success_page' with the name of your success URL or view
    else:
        form = FormularioTombolaForm()
    
    return render(request, 'formularioTombola.html', {'form': form})