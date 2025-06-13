from django.http import JsonResponse
from .models import ClienteEntrevista

def entrevistas_json(request):
    entrevistas = list(ClienteEntrevista.objects.all().values())
    response = {
        "status": "success",
        "total": len(entrevistas),
        "data": entrevistas
    }
    return JsonResponse(response, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})
