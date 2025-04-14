from django.http import JsonResponse
from .models import Boleto, Cliente

def fetch_boletos_by_cedula(request):
    cedula = request.GET.get('cedula')  # Get the cedula from the request
    try:
        cliente = Cliente.objects.get(cedulaCliente=cedula)  # Find the cliente by cedula
        boletos = Boleto.objects.filter(cliente=cliente)  # Get boletos related to the cliente
        boletos_data = [
            {
                'id': boleto.id,
                'fecha_creacion': boleto.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                'tombola': boleto.tombola.id,
                'canalOrigen': boleto.canalOrigen,
            }
            for boleto in boletos
        ]
        return JsonResponse({'success': True, 'boletos': boletos_data})
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente no encontrado.'})