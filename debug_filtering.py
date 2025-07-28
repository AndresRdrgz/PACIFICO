from workflow.modelsWorkflow import Solicitud, Pipeline
from django.contrib.auth.models import User
from django.db.models import Q

print("=== SOLICITUDES FILTERING DEBUG ===")

# Get the superuser
user = User.objects.filter(is_superuser=True).first()
print(f"Testing with user: {user} (superuser: {user.is_superuser})")

# Test superuser filtering logic
if user.is_superuser:
    print("\n🔍 SUPERUSER LOGIC:")
    solicitudes = Solicitud.objects.select_related(
        'pipeline', 'etapa_actual', 'subestado_actual', 
        'creada_por', 'asignada_a'
    ).prefetch_related(
        'cliente', 'cotizacion'
    ).all()
    print(f"  All solicitudes count: {solicitudes.count()}")
    for s in solicitudes:
        print(f"    - {s.codigo}: Created by {s.creada_por}, Assigned to {s.asignada_a}")
else:
    print("\n🔍 REGULAR USER LOGIC:")
    solicitudes = Solicitud.objects.select_related(
        'pipeline', 'etapa_actual', 'subestado_actual', 
        'creada_por', 'asignada_a'
    ).prefetch_related(
        'cliente', 'cotizacion'
    ).filter(
        Q(asignada_a=user) | Q(creada_por=user)
    )
    print(f"  Filtered solicitudes count: {solicitudes.count()}")

# Test with pipeline filter
pipeline_filter = '12'
if pipeline_filter:
    print(f"\n🔍 WITH PIPELINE FILTER ({pipeline_filter}):")
    filtered_solicitudes = solicitudes.filter(pipeline_id=pipeline_filter)
    print(f"  Filtered by pipeline solicitudes count: {filtered_solicitudes.count()}")
    for s in filtered_solicitudes:
        print(f"    - {s.codigo}: Pipeline {s.pipeline.nombre}")

print("\n=== END DEBUG ===")
