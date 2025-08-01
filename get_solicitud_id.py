import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud

try:
    solicitud = Solicitud.objects.get(codigo='FLU-132')
    print(f"Solicitud FLU-132:")
    print(f"  ID: {solicitud.pk}")
    print(f"  Código: {solicitud.codigo}")
    print(f"  resultado_consulta: '{solicitud.resultado_consulta}'")
    print(f"  Correct API URL: /workflow/api/solicitudes/{solicitud.pk}/pdf-resultado-consulta/")
except Exception as e:
    print(f"Error: {e}")
