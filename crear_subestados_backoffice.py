# ========================================
# CÓDIGO PARA CREAR SUBESTADOS EN DJANGO
# ========================================

# 1. Abre el shell de Django (después de activar el entorno):
# python manage.py shell

# 2. Ejecuta este código línea por línea:

from workflow.modelsWorkflow import Etapa, SubEstado

# Buscar la etapa de Back Office (ajusta el nombre si es diferente)
etapa_backoffice = Etapa.objects.filter(nombre__icontains='back office').first()

if not etapa_backoffice:
    # Si no encuentra por "back office", buscar por otros nombres posibles
    etapa_backoffice = Etapa.objects.filter(nombre__icontains='backoffice').first()
    
if not etapa_backoffice:
    print("❌ No se encontró la etapa de Back Office")
    print("Etapas disponibles:")
    for etapa in Etapa.objects.all():
        print(f"  - {etapa.nombre}")
else:
    print(f"✅ Etapa encontrada: {etapa_backoffice.nombre}")
    
    # Crear los 4 subestados
    subestados = [
        {'nombre': 'Checklist', 'orden': 1},
        {'nombre': 'Captura', 'orden': 2}, 
        {'nombre': 'Firma', 'orden': 3},
        {'nombre': 'Orden del expediente', 'orden': 4}
    ]
    
    for data in subestados:
        subestado, created = SubEstado.objects.get_or_create(
            etapa=etapa_backoffice,
            nombre=data['nombre'],
            defaults={'orden': data['orden']}
        )
        if created:
            print(f"✅ Creado: {subestado.nombre}")
        else:
            print(f"⚠️ Ya existe: {subestado.nombre}")
    
    print(f"\n🎉 ¡Subestados configurados para {etapa_backoffice.nombre}!")
