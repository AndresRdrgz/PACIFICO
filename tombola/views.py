from django.shortcuts import render, redirect
from .forms import FormularioTombolaForm
from .models import FormularioTombola, Boleto

# Create your views here.
def moduloTombola(request):
    tombola_list = FormularioTombola.objects.all()
    boleto_list = Boleto.objects.all()  # Assuming you have a model named Boleto
    return render(request, 'moduloTombola.html', {'tombola_list': tombola_list, 'boleto_list': boleto_list})

def formularioTombola(request):
    if request.method == 'POST':
        form = FormularioTombolaForm(request.POST)
        if form.is_valid():
            formulario = form.save()  # Save the FormularioTombola instance
            boleto = Boleto.objects.create(
                tombola=formulario.tombola,  # Assuming FormularioTombola has a tombola ForeignKey
                canalOrigen='Formulario'  # Set the canalOrigen field
            )
            return redirect('confirmacion', boleto_id=boleto.id)  # Redirect to confirmation page with boleto_id
    else:
        form = FormularioTombolaForm()
    
    return render(request, 'formularioTombola.html', {'form': form})

def confirmacion(request, boleto_id):
    return render(request, 'confirmacion.html', {'boleto_id': boleto_id})