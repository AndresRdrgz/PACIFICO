#!/usr/bin/env python
"""
Script de demostración para relacionar una entrevista con una solicitud
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from workflow.modelsWorkflow import Solicitud
from workflow.models import ClienteEntrevista

def demo_relacion_entrevista():
    """
    Demuestra cómo relacionar una entrevista con una solicitud
    """
    print("🎯 DEMOSTRACIÓN: Relacionar entrevista con solicitud")
    print("="*60)
    
    # 1. Mostrar solicitudes actuales
    solicitudes = Solicitud.objects.all()
    print(f"\n📝 Solicitudes disponibles ({solicitudes.count()}):")
    for solicitud in solicitudes[:3]:
        entrevista_info = f" -> Entrevista: {solicitud.entrevista_cliente}" if solicitud.entrevista_cliente else " -> Sin entrevista"
        print(f"   ID: {solicitud.id} | Código: {solicitud.codigo}{entrevista_info}")
    
    # 2. Mostrar entrevistas disponibles
    entrevistas = ClienteEntrevista.objects.all()
    print(f"\n👤 Entrevistas disponibles ({entrevistas.count()}):")
    for entrevista in entrevistas[:3]:
        solicitudes_count = entrevista.solicitudes.count()
        print(f"   ID: {entrevista.id} | Cliente: {entrevista.primer_nombre} {entrevista.primer_apellido} | Solicitudes: {solicitudes_count}")
    
    # 3. Ejemplo de relación
    if solicitudes.exists() and entrevistas.exists():
        solicitud = solicitudes.first()
        entrevista = entrevistas.first()
        
        print(f"\n🔗 Ejemplo de relación:")
        print(f"   Solicitud: {solicitud.codigo}")
        print(f"   Cliente entrevista: {entrevista.primer_nombre} {entrevista.primer_apellido}")
        
        # Mostrar cómo se haría la relación (sin ejecutar para no modificar datos)
        print(f"\n💡 Para relacionar en código:")
        print(f"   solicitud = Solicitud.objects.get(id={solicitud.id})")
        print(f"   entrevista = ClienteEntrevista.objects.get(id={entrevista.id})")
        print(f"   solicitud.entrevista_cliente = entrevista")
        print(f"   solicitud.save()")
        
        print(f"\n💡 Para relacionar en el admin:")
        print(f"   1. Ir a /admin/workflow/solicitud/{solicitud.id}/change/")
        print(f"   2. En la sección 'Datos del Cliente', usar el campo 'Entrevista cliente'")
        print(f"   3. Buscar y seleccionar la entrevista deseada")
        print(f"   4. Guardar la solicitud")
    
    # 4. Mostrar información de campos relacionados
    print(f"\n📊 Información de campos relacionados:")
    print(f"   • Solicitud.entrevista_cliente -> ClienteEntrevista (opcional)")
    print(f"   • ClienteEntrevista.solicitudes -> Múltiples Solicitudes")
    print(f"   • Relación: One-to-Many (Una entrevista puede tener múltiples solicitudes)")
    
    # 5. Consultas útiles
    print(f"\n🔍 Consultas útiles:")
    print(f"   # Solicitudes con entrevista")
    solicitudes_con_entrevista = Solicitud.objects.filter(entrevista_cliente__isnull=False).count()
    print(f"   Solicitud.objects.filter(entrevista_cliente__isnull=False).count() = {solicitudes_con_entrevista}")
    
    print(f"   # Solicitudes sin entrevista")
    solicitudes_sin_entrevista = Solicitud.objects.filter(entrevista_cliente__isnull=True).count()
    print(f"   Solicitud.objects.filter(entrevista_cliente__isnull=True).count() = {solicitudes_sin_entrevista}")
    
    print(f"   # Entrevistas con solicitudes")
    entrevistas_con_solicitudes = ClienteEntrevista.objects.filter(solicitudes__isnull=False).distinct().count()
    print(f"   ClienteEntrevista.objects.filter(solicitudes__isnull=False).distinct().count() = {entrevistas_con_solicitudes}")
    
    print(f"\n✨ Demostración completa!")

if __name__ == "__main__":
    demo_relacion_entrevista()
