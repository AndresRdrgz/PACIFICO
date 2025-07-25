#!/usr/bin/env python
"""
Script para arreglar los datos de cédula corruptos
"""
import os
import sys
import django

# Agregar el path del proyecto
sys.path.append('c:/Users/jacastillo/Documents/GitHub/PACIFICO')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import ClienteEntrevista

# Buscar entrevistas con datos corruptos
entrevistas = ClienteEntrevista.objects.all()
print(f"Total entrevistas: {entrevistas.count()}")

for entrevista in entrevistas:
    print(f"\n=== ENTREVISTA {entrevista.id} ===")
    print(f"Nombre: {entrevista.primer_nombre} {entrevista.primer_apellido}")
    print(f"ANTES - Provincia: {entrevista.provincia_cedula}")
    print(f"ANTES - Tipo letra: {entrevista.tipo_letra}")
    print(f"ANTES - Tomo: {entrevista.tomo_cedula}")
    print(f"ANTES - Partida: {entrevista.partida_cedula}")
    
    # Verificar si los datos están corruptos (contienen fechas u otros datos extraños)
    datos_corruptos = False
    
    # Si provincia_cedula contiene algo que no sea un número de 1-2 dígitos
    if entrevista.provincia_cedula and not entrevista.provincia_cedula.isdigit():
        print("⚠️ DATO CORRUPTO: provincia_cedula no es numérico")
        entrevista.provincia_cedula = "8"  # Default a Panamá
        datos_corruptos = True
    
    # Si tipo_letra contiene algo que no sea una letra válida
    letras_validas = ['A', 'AV', 'E', 'N', 'P', 'PI', 'PE']
    if entrevista.tipo_letra and entrevista.tipo_letra not in letras_validas:
        print("⚠️ DATO CORRUPTO: tipo_letra no es válido")
        entrevista.tipo_letra = "E"  # Default
        datos_corruptos = True
    
    # Si tomo_cedula contiene datos extraños
    if entrevista.tomo_cedula and not entrevista.tomo_cedula.replace('-', '').isdigit():
        print("⚠️ DATO CORRUPTO: tomo_cedula no es numérico")
        entrevista.tomo_cedula = "0000"  # Default
        datos_corruptos = True
    
    # Si partida_cedula contiene datos extraños
    if entrevista.partida_cedula and not entrevista.partida_cedula.replace('-', '').isdigit():
        print("⚠️ DATO CORRUPTO: partida_cedula no es numérico")
        entrevista.partida_cedula = "99999"  # Default
        datos_corruptos = True
    
    if datos_corruptos:
        print("🔧 CORRIGIENDO DATOS...")
        entrevista.save()
        print(f"DESPUÉS - Provincia: {entrevista.provincia_cedula}")
        print(f"DESPUÉS - Tipo letra: {entrevista.tipo_letra}")
        print(f"DESPUÉS - Tomo: {entrevista.tomo_cedula}")
        print(f"DESPUÉS - Partida: {entrevista.partida_cedula}")
    else:
        print("✅ Datos OK")

print("\n✅ Script completado")
