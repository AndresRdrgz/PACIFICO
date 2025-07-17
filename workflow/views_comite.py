from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .modelsWorkflow import Solicitud, Etapa, ParticipacionComite, NivelComite, UsuarioNivelComite
from django.http import JsonResponse
from django.core.paginator import Paginator

@login_required
def bandeja_comite_view(request):
    """
    Renderiza la bandeja de trabajo del Comité de Crédito.
    """
    
    # Por ahora, solo superuser puede ver todo.
    # La lógica de permisos por nivel se implementará en la API.
    if not request.user.is_superuser:
        # Aquí iría la lógica para usuarios que no son superusuarios
        # Por ejemplo, verificar si pertenecen a algún nivel del comité.
        pass

    # Obtener la etapa "Comité de Crédito"
    try:
        etapa_comite = Etapa.objects.get(nombre__iexact="Comité de Crédito")
        # Calcular la cantidad de solicitudes en la etapa del comité
        total_solicitudes = Solicitud.objects.filter(etapa_actual=etapa_comite).count()
    except Etapa.DoesNotExist:
        # Si no existe la etapa, no hay nada que mostrar.
        # Se puede agregar un mensaje para el admin.
        etapa_comite = None
        total_solicitudes = 0

    context = {
        'etapa_comite': etapa_comite,
        'total_solicitudes': total_solicitudes,
        'page_title': 'Bandeja del Comité de Crédito',
        'page_description': 'Solicitudes pendientes de revisión y aprobación por el comité.'
    }
    
    return render(request, 'workflow/bandeja_comite.html', context) 