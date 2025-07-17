import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Pipeline, Etapa, NivelComite, UsuarioNivelComite
from django.contrib.auth.models import User
from datetime import timedelta

print("🏗️  Configurando datos iniciales del Comité de Crédito...")

# 1. Crear niveles de comité básicos
print("\n🏗️  Configurando niveles de comité...")

niveles_comite = [
    {'nombre': 'Supervisor de Crédito', 'orden': 1},
    {'nombre': 'Gerente de Crédito', 'orden': 2},
    {'nombre': 'Gerente General', 'orden': 3},
    {'nombre': 'Director', 'orden': 4},
]

for nivel_data in niveles_comite:
    nivel, created = NivelComite.objects.get_or_create(
        nombre=nivel_data['nombre'],
        defaults={'orden': nivel_data['orden']}
    )
    if created:
        print(f"✅ Nivel creado: {nivel.nombre}")
    else:
        print(f"⚠️  Nivel ya existe: {nivel.nombre}")

# 2. Crear etapa "Comité de Crédito" en los pipelines existentes
print("\n🏗️  Configurando etapas del comité...")

pipelines = Pipeline.objects.all()
if not pipelines.exists():
    print("⚠️  No hay pipelines configurados. Creando pipeline de ejemplo...")
    pipeline = Pipeline.objects.create(
        nombre="Préstamo Personal",
        descripcion="Pipeline para préstamos personales"
    )
    print(f"✅ Pipeline creado: {pipeline.nombre}")
    pipelines = [pipeline]

for pipeline in pipelines:
    etapa_comite, created = Etapa.objects.get_or_create(
        pipeline=pipeline,
        nombre="Comité de Crédito",
        defaults={
            'orden': 50,
            'sla': timedelta(hours=72),
            'es_bandeja_grupal': True
        }
    )
    if created:
        print(f"✅ Etapa creada: {etapa_comite.nombre} en {pipeline.nombre}")
    else:
        print(f"⚠️  Etapa ya existe: {etapa_comite.nombre} en {pipeline.nombre}")

# 3. Asignar superusuario al nivel más alto
print("\n🏗️  Configurando usuarios del comité...")

superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    nivel_mas_alto = NivelComite.objects.order_by('-orden').first()
    if nivel_mas_alto:
        for superuser in superusers:
            usuario_nivel, created = UsuarioNivelComite.objects.get_or_create(
                usuario=superuser,
                nivel=nivel_mas_alto,
                defaults={'activo': True}
            )
            if created:
                print(f"✅ Usuario asignado: {superuser.username} a {nivel_mas_alto.nombre}")
            else:
                print(f"⚠️  Usuario ya asignado: {superuser.username} a {nivel_mas_alto.nombre}")

print("\n🎉 ¡Configuración del comité completada!")
print("\n📋 Pasos siguientes:")
print("1. Ir al admin de Django para configurar más niveles si es necesario")
print("2. Asignar usuarios específicos a los niveles del comité")
print("3. Crear transiciones hacia y desde la etapa 'Comité de Crédito'")
print("4. Probar la funcionalidad en /workflow/comite/") 