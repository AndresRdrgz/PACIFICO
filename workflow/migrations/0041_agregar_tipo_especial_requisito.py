# Generated manually for adding tipo_especial field to Requisito model

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0040_agregar_requisito_agendar_firma'),
    ]

    operations = [
        migrations.AddField(
            model_name='requisito',
            name='tipo_especial',
            field=models.CharField(
                max_length=50, 
                blank=True, 
                null=True, 
                help_text="Tipo especial de requisito (agenda_firma, etc.)",
                choices=[
                    ('agenda_firma', 'Agenda de Firma'),
                ]
            ),
        ),
    ]