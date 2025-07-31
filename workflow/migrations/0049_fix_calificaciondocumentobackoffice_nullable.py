# Generated manually to fix calificaciondocumentobackoffice field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0048_merge_20250731_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud',
            name='calificaciondocumentobackoffice',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('bueno', 'Bueno'),
                    ('malo', 'Malo')
                ],
                help_text='Estado de la calificación de documentos en Back Office (solo se activa al llegar a Back Office)',
                max_length=20,
                null=True
            ),
        ),
    ]