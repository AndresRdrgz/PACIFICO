from workflow.modelsWorkflow import Solicitud, Pipeline
from django.contrib.auth.models import User

print("=== SOLICITUDES DEBUG ===")

# Check total solicitudes
total_solicitudes = Solicitud.objects.count()
print(f"Total solicitudes: {total_solicitudes}")

# Check solicitudes by pipeline
print(f"Solicitudes by pipeline:")
for p in Pipeline.objects.all():
    count = Solicitud.objects.filter(pipeline=p).count()
    print(f"  - {p.nombre} (ID: {p.pk}): {count} solicitudes")

# Check recent solicitudes
print("Recent solicitudes:")
for s in Solicitud.objects.order_by('-fecha_creacion')[:5]:
    pipeline_name = s.pipeline.nombre if s.pipeline else "None"
    print(f"  - {s.codigo}: Pipeline {pipeline_name}, Created: {s.fecha_creacion}")

# Check user who created solicitudes
print("Solicitudes by user:")
user = User.objects.filter(is_superuser=True).first()
if user:
    user_solicitudes = Solicitud.objects.filter(creada_por=user).count()
    assigned_solicitudes = Solicitud.objects.filter(asignada_a=user).count()
    print(f"  - Created by {user}: {user_solicitudes}")
    print(f"  - Assigned to {user}: {assigned_solicitudes}")

print("=== END DEBUG ===")
