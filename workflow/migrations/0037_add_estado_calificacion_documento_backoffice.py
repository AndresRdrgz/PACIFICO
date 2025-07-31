# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0036_merge_20250725_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='estado_calificacion_documento_backoffice',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('bueno', 'Bueno'),
                    ('malo', 'Malo')
                ],
                default='pendiente',
                help_text='Estado de la calificación de documentos en Back Office',
                max_length=20
            ),
        ),
    ]
