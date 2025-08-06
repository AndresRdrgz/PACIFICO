# Generated manually for adding "Agendar Firma" requirement

from django.db import migrations

def crear_requisito_agendar_firma(apps, schema_editor):
    """Crear el requisito 'Agendar Firma'"""
    Requisito = apps.get_model('workflow', 'Requisito')
    
    # Crear el nuevo requisito (sin tipo_especial por ahora)
    requisito, created = Requisito.objects.get_or_create(
        nombre="Agendar Firma",
        defaults={
            'descripcion': 'Requisito para agendar una cita de firma de documentos'
        }
    )
    
    if created:
        print(f"✅ Requisito 'Agendar Firma' creado con ID: {requisito.id}")
    else:
        print(f"ℹ️ Requisito 'Agendar Firma' ya existe con ID: {requisito.id}")

def eliminar_requisito_agendar_firma(apps, schema_editor):
    """Eliminar el requisito 'Agendar Firma'"""
    Requisito = apps.get_model('workflow', 'Requisito')
    
    try:
        requisito = Requisito.objects.get(nombre="Agendar Firma")
        requisito.delete()
        print("✅ Requisito 'Agendar Firma' eliminado")
    except Requisito.DoesNotExist:
        print("ℹ️ Requisito 'Agendar Firma' no existe")

class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0039_agregar_agenda_firma'),
    ]

    operations = [
        migrations.RunPython(
            crear_requisito_agendar_firma,
            eliminar_requisito_agendar_firma
        ),
    ]