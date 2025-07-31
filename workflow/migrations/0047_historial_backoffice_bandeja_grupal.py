# Generated manually to add bandeja grupal functionality
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0046_historial_backoffice'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add new fields for bandeja grupal functionality
        migrations.AddField(
            model_name='historialbackoffice',
            name='fecha_asignacion_bandeja_grupal',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Asignación desde Bandeja Grupal'),
        ),
        migrations.AddField(
            model_name='historialbackoffice',
            name='fecha_entrada_bandeja_grupal',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Entrada a Bandeja Grupal'),
        ),
        migrations.AddField(
            model_name='historialbackoffice',
            name='tiempo_en_bandeja_grupal',
            field=models.DurationField(blank=True, null=True, verbose_name='Tiempo en Bandeja Grupal'),
        ),
        migrations.AddField(
            model_name='historialbackoffice',
            name='usuario_asignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones_backoffice', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Asignado (para eventos de asignación)'),
        ),
        # Update tipo_evento choices to include new events
        migrations.AlterField(
            model_name='historialbackoffice',
            name='tipo_evento',
            field=models.CharField(
                choices=[
                    ('devolucion', 'Devolución a Negocio'), 
                    ('calificacion', 'Cambio de Calificación'), 
                    ('subestado', 'Cambio de Subestado'), 
                    ('entrada_bandeja_grupal', 'Entrada a Bandeja Grupal'), 
                    ('asignacion_desde_bandeja_grupal', 'Asignación desde Bandeja Grupal')
                ], 
                max_length=35, 
                verbose_name='Tipo de Evento'
            ),
        ),
    ]