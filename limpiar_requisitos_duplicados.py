#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import RequisitoTransicion, Pipeline

def limpiar_requisitos_duplicados():
    # Obtener pipeline
    pipeline = Pipeline.objects.get(id=18)
    print(f"Pipeline: {pipeline.nombre}")
    
    # Obtener todos los requisitos del pipeline
    requisitos = RequisitoTransicion.objects.filter(transicion__pipeline=pipeline)
    print(f"Total requisitos encontrados: {len(requisitos)}")
    
    # Agrupar por nombre de requisito
    requisitos_por_nombre = {}
    for rt in requisitos:
        nombre = rt.requisito.nombre
        if nombre not in requisitos_por_nombre:
            requisitos_por_nombre[nombre] = []
        requisitos_por_nombre[nombre].append(rt)
    
    print("\nRequisitos agrupados:")
    duplicados_eliminados = 0
    
    for nombre, lista_rt in requisitos_por_nombre.items():
        print(f"\n- {nombre}: {len(lista_rt)} instancias")
        
        if len(lista_rt) > 1:
            # Mostrar todas las instancias
            for i, rt in enumerate(lista_rt):
                print(f"  [{i}] ID: {rt.id} - Obligatorio: {rt.obligatorio} - Transicion: {rt.transicion.id}")
            
            # Mantener solo la primera instancia, eliminar las demás
            for i in range(1, len(lista_rt)):
                rt = lista_rt[i]
                print(f"  ❌ Eliminando duplicado ID: {rt.id}")
                rt.delete()
                duplicados_eliminados += 1
        else:
            rt = lista_rt[0]
            print(f"  ✅ ID: {rt.id} - Obligatorio: {rt.obligatorio}")
    
    print(f"\n✅ Eliminados {duplicados_eliminados} requisitos duplicados")
    
    # Verificar resultado final
    requisitos_finales = RequisitoTransicion.objects.filter(transicion__pipeline=pipeline)
    print(f"\nRequisitos finales: {len(requisitos_finales)}")
    for rt in requisitos_finales:
        print(f"- {rt.requisito.nombre} (ID: {rt.requisito.id}) - Obligatorio: {rt.obligatorio}")

if __name__ == "__main__":
    limpiar_requisitos_duplicados()
