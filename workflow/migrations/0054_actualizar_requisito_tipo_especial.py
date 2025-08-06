# Generated manually for updating Agendar Firma requirement with tipo_especial

from django.db import migrations

def actualizar_requisito_tipo_especial(apps, schema_editor):
    """Actualizar el requisito 'Agendar Firma' con tipo_especial"""
    Requisito = apps.get_model('workflow', 'Requisito')
    
    try:
        requisito = Requisito.objects.get(nombre="Agendar Firma")
        requisito.tipo_especial = 'agenda_firma'
        requisito.save()
        print(f"✅ Requisito 'Agendar Firma' actualizado con tipo_especial: {requisito.tipo_especial}")
    except Requisito.DoesNotExist:
        print("⚠️ Requisito 'Agendar Firma' no encontrado para actualizar")

def revertir_requisito_tipo_especial(apps, schema_editor):
    """Revertir el tipo_especial del requisito 'Agendar Firma'"""
    Requisito = apps.get_model('workflow', 'Requisito')
    
    try:
        requisito = Requisito.objects.get(nombre="Agendar Firma")
        requisito.tipo_especial = None
        requisito.save()
        print("✅ Tipo especial del requisito 'Agendar Firma' revertido")
    except Requisito.DoesNotExist:
        print("⚠️ Requisito 'Agendar Firma' no encontrado para revertir")

class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0053_merge_20250806_1609'),
    ]

    operations = [
        migrations.RunPython(
            actualizar_requisito_tipo_especial,
            revertir_requisito_tipo_especial
        ),
    ]