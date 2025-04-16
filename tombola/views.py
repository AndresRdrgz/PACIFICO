import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import FormularioTombolaForm
from .models import FormularioTombola, Boleto
from pacifico.models import Cliente

# Create your views here.
def moduloTombola(request):
    tombola_list = FormularioTombola.objects.all()
    boleto_list = Boleto.objects.all()  # Assuming you have a model named Boleto
    return render(request, 'moduloTombola.html', {'tombola_list': tombola_list, 'boleto_list': boleto_list})

def formularioTombola(request):
    try:
        if request.method == 'POST':
            form = FormularioTombolaForm(request.POST)
            if form.is_valid():
                print("Formulario válido")
                formulario = form.save()  # Save the FormularioTombola instance
                
                # Check if Cliente with given cedula exists, otherwise create it
                cedulaCliente = form.cleaned_data.get('cedulaCliente')  # Assuming the form has a 'cedula' field
                nombre = form.cleaned_data.get('nombre')  # Assuming the form has a 'nombre' field
                apellido = form.cleaned_data.get('apellido')  # Assuming the form has an 'apellido' field
                edad = form.cleaned_data.get('edad')  # Assuming the form has an 'edad' field
                sexo = form.cleaned_data.get('sexo')  # Assuming the form has a 'sexo' field
                
                cliente, created = Cliente.objects.get_or_create(
                    cedulaCliente=cedulaCliente,
                    defaults={
                        'nombreCliente': f"{nombre} {apellido}",
                        'edad': edad,
                        'sexo': sexo
                    }
                )

                # Check if a Boleto already exists for this tombola, cedula, and origin
                existing_boleto = Boleto.objects.filter(
                    tombola=formulario.tombola,
                    cliente=cliente,
                    canalOrigen='Formulario'
                ).first()
                print(f"Existing Boleto: {existing_boleto}")
                if existing_boleto:
                    print("Cliente ya está participando")
                    return render(request, 'confirmacion.html', {
                        'error_message': "Cliente ya está participando",
                    })

                # Create the Boleto instance
                boleto = Boleto.objects.create(
                    tombola=formulario.tombola,  # Assuming FormularioTombola has a tombola ForeignKey
                    cliente=cliente,  # Associate the Boleto with the Cliente
                    canalOrigen='Formulario'  # Set the canalOrigen field
                )

                return redirect('confirmacion', boleto_id=boleto.id)  # Redirect to confirmation page with boleto_id
        else:
            form = FormularioTombolaForm()
        
        return render(request, 'formularioTombola.html', {'form': form})
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'formularioTombola.html', {
            'form': FormularioTombolaForm(),
            'error_message': "Ocurrió un error al procesar el formulario. Por favor, inténtelo de nuevo."
        })

def confirmacion(request, boleto_id):
    return render(request, 'confirmacion.html', {'boleto_id': boleto_id})

def validadorCedula(request):
    return render(request, 'validadorCedula.html')

