# Generated migration for adding archivo_adjunto field to ReconsideracionSolicitud

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0045_add_orden_seccion_field'),  # Updated to actual last migration
    ]

    operations = [
        migrations.AddField(
            model_name='reconsideracionsolicitud',
            name='archivo_adjunto',
            field=models.FileField(
                blank=True,
                help_text='Archivo PDF adjunto a la reconsideración',
                null=True,
                upload_to='reconsideraciones/'
            ),
        ),
    ]
