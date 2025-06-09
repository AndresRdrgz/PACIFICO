from django.http import JsonResponse
from .models import ClienteEntrevista

def entrevistas_json(request):
    entrevistas = ClienteEntrevista.objects.all().values()
    return JsonResponse(list(entrevistas), safe=False)
