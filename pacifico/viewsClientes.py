from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cliente, Cotizacion, UserProfile
from .formsClientes import ClienteForm, EditClienteForm
from .filtersClientes import ClienteFilter
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages



@login_required
def cliente_profile(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cotizaciones = Cotizacion.objects.filter(cedulaCliente=cliente.cedulaCliente).order_by('-created_at')

    # Filter cotizaciones based on user unless they're staff
    if request.user.is_authenticated and not request.user.is_staff:
        cotizaciones = cotizaciones.filter(added_by=request.user)
    
    if request.method == 'POST':
        form = EditClienteForm(request.POST, instance=cliente, user=request.user)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Los datos del cliente {cliente.nombreCliente} han sido actualizados correctamente.')
            return redirect('cliente_profile', id=cliente.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = EditClienteForm(instance=cliente, user=request.user)

    context = {
        'cliente': cliente,
        'cotizaciones': cotizaciones,
        'form': form,
        'tab_active': request.GET.get('tab', 'datos'),
    }
    return render(request, 'clientes/cliente_profile.html', context)

@login_required
def clientesList(request):
    # Get user profile to check role
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_rol = user_profile.rol
    except UserProfile.DoesNotExist:
        user_rol = 'Supervisor'  # Default role if no profile exists
    
    # Filter clients based on user role and group supervision
    if user_rol in ['Oficial', 'Asistente']:
        # Usar la función centralizada para obtener datos visibles
        from .utils_grupos import obtener_todos_los_datos_visibles_para_usuario
        clientes = obtener_todos_los_datos_visibles_para_usuario(request.user, Cliente).order_by('-id')
    else:
        # All other users can see all clients
        clientes = Cliente.objects.all().order_by('-id')
    
    # Apply filter only for Supervisors and Administrators
    cliente_filter = ClienteFilter(request.GET, queryset=clientes, user=request.user)
    clientes = cliente_filter.qs
    
    # Check if user can see the filter
    # Usar la función centralizada para verificar si es supervisor efectivo
    from .utils_grupos import es_supervisor_efectivo
    
    show_filter = (
        user_rol in ['Supervisor', 'Administrador'] or 
        es_supervisor_efectivo(request.user) or
        request.user.is_superuser
    )
    
    context = {
        'clientes': clientes,
        'filter': cliente_filter,
        'show_filter': show_filter,
    }
    
    return render(request, 'clientes/clientesList.html', context)

@login_required
@csrf_exempt
def cliente_create(request):
    # Handle AJAX GET: return form HTML
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ClienteForm(user=request.user)
        html = render_to_string('clientes/partials/cliente_form.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    # Handle POST submission
    if request.method == 'POST':
        form = ClienteForm(request.POST, user=request.user)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.added_by = request.user
            cliente.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                data = {
                    'id': cliente.id,
                    'cedulaCliente': cliente.cedulaCliente or '',
                    'nombreCliente': cliente.nombreCliente
                }
                return JsonResponse({'success': True, 'cliente': data})
            return redirect('clientesList')
        else:
            # Return form with errors for AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('clientes/partials/cliente_form.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'html': html})
    # Non-AJAX GET or fallback
    form = ClienteForm(user=request.user)
    return render(request, 'clientes/partials/cliente_form.html', {'form': form})
