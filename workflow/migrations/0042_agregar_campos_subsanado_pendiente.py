# Generated manually for adding subsanado_por_oficial and pendiente_completado fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0041_add_subsanado_to_calificacion_documento_backoffice'),
    ]

    operations = [
        migrations.AddField(
            model_name='calificaciondocumentobackoffice',
            name='subsanado_por_oficial',
            field=models.BooleanField(default=False, help_text='Indica si la oficial ya subió/reemplazó el documento para subsanar el problema', verbose_name='Subsanado por Oficial'),
        ),
        migrations.AddField(
            model_name='calificaciondocumentobackoffice',
            name='pendiente_completado',
            field=models.BooleanField(default=False, help_text='Indica si la oficial ya subió archivo para un documento que estaba pendiente', verbose_name='Pendiente Completado'),
        ),
    ]