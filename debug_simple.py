# Simple shell command to debug pipelines
from workflow.modelsWorkflow import Pipeline, PermisoPipeline
from django.contrib.auth.models import User

print("=== PIPELINE PERMISSIONS DEBUG ===")

# Get the superuser
user = User.objects.filter(is_superuser=True).first()
print(f"Superuser found: {user}")
print(f"Is superuser: {user.is_superuser if user else 'No user found'}")

# Check all pipelines
pipelines = Pipeline.objects.all()
print(f"Total pipelines in database: {pipelines.count()}")
for p in pipelines:
    print(f"  - Pipeline: '{p.nombre}' (ID: {p.pk})")

# Check permissions
permisos = PermisoPipeline.objects.all()
print(f"Total pipeline permissions: {permisos.count()}")

print("=== DEBUG COMPLETE ===")
