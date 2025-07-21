#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud, Etapa

print("=== VERIFICACIÓN DE ETAPAS Y SOLICITUDES ===")
print()

# Verificar etapas disponibles
print("Etapas disponibles:")
etapas = Etapa.objects.all()
for etapa in etapas:
    print(f"- {etapa.nombre} (ID: {etapa.id})")
print()

# Buscar etapa del comité
comite = Etapa.objects.filter(nombre__iexact='Comité de Crédito').first()
print(f"Etapa Comité de Crédito: {comite}")
print()

if comite:
    # Verificar solicitudes en comité
    solicitudes = Solicitud.objects.filter(etapa_actual=comite)
    print(f"Total solicitudes en comité: {solicitudes.count()}")
    print()
    
    for solicitud in solicitudes:
        print(f"- Código: {solicitud.codigo}")
        print(f"  ID: {solicitud.id}")
        print(f"  Cliente: {getattr(solicitud, 'cliente_nombre', 'Sin cliente')}")
        print(f"  Creada por: {solicitud.creada_por}")
        print(f"  Fecha: {solicitud.fecha_creacion}")
        print()
else:
    print("❌ No se encontró la etapa 'Comité de Crédito'")
    print()
    print("Etapas que contienen 'comité':")
    etapas_comite = Etapa.objects.filter(nombre__icontains='comité')
    for etapa in etapas_comite:
        print(f"- {etapa.nombre}")

print("=== FIN DE VERIFICACIÓN ===") 