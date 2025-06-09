from django.shortcuts import render, redirect
from .forms import ClienteEntrevistaForm
from .models import ClienteEntrevista

def entrevista_cliente(request):
    if request.method == 'POST':
        form = ClienteEntrevistaForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'workflow/entrevista_exito.html')
    else:
        form = ClienteEntrevistaForm()
    return render(request, 'workflow/entrevista_cliente.html', {'form': form})

def lista_entrevistas(request):
    entrevistas = ClienteEntrevista.objects.all().order_by('-fecha_entrevista')
    return render(request, 'workflow/lista_entrevistas.html', {'entrevistas': entrevistas})
