#!/usr/bin/env python
"""
Script para poblar opciones de desplegable de ejemplo
para la calificación de documentos en el workflow
"""
import os
import sys
import django

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
    django.setup()

from workflow.models import OpcionDesplegable

def create_opciones_ejemplo():
    """Crear opciones de ejemplo para el desplegable"""
    
    opciones_ejemplo = [
        {
            'nombre': 'Documento ilegible',
            'descripcion': 'El documento no se puede leer claramente',
            'orden': 1
        },
        {
            'nombre': 'Falta información',
            'descripcion': 'Información requerida no está presente en el documento',
            'orden': 2
        },
        {
            'nombre': 'Documento vencido',
            'descripcion': 'El documento está fuera de fecha de vigencia',
            'orden': 3
        },
        {
            'nombre': 'Formato incorrecto',
            'descripcion': 'El documento no está en el formato requerido',
            'orden': 4
        },
        {
            'nombre': 'Firma faltante',
            'descripcion': 'El documento requiere firma pero no la tiene',
            'orden': 5
        },
        {
            'nombre': 'Datos inconsistentes',
            'descripcion': 'Los datos del documento no coinciden con otros documentos',
            'orden': 6
        },
        {
            'nombre': 'Calidad de imagen deficiente',
            'descripcion': 'La imagen o escaneo es de muy baja calidad',
            'orden': 7
        },
        {
            'nombre': 'Documento incompleto',
            'descripcion': 'Faltan páginas o secciones del documento',
            'orden': 8
        },
        {
            'nombre': 'Requiere certificación',
            'descripcion': 'El documento necesita estar certificado o apostillado',
            'orden': 9
        },
        {
            'nombre': 'Otros motivos',
            'descripcion': 'Otros motivos no especificados arriba',
            'orden': 10
        }
    ]
    
    created_count = 0
    
    for opcion_data in opciones_ejemplo:
        opcion, created = OpcionDesplegable.objects.get_or_create(
            nombre=opcion_data['nombre'],
            defaults={
                'descripcion': opcion_data['descripcion'],
                'orden': opcion_data['orden'],
                'activo': True
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Creada opción: {opcion.nombre}")
        else:
            print(f"⏭️  Ya existe: {opcion.nombre}")
    
    print(f"\n🎉 Proceso completado. {created_count} nuevas opciones creadas.")
    print(f"📊 Total de opciones activas: {OpcionDesplegable.objects.filter(activo=True).count()}")

if __name__ == "__main__":
    print("🚀 Iniciando población de opciones de desplegable...")
    create_opciones_ejemplo()
