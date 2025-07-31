# Generated manually to avoid field removal conflicts
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0045_add_orden_seccion_field'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialBackoffice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_evento', models.CharField(choices=[('devolucion', 'Devolución a Negocio'), ('calificacion', 'Cambio de Calificación'), ('subestado', 'Cambio de Subestado')], max_length=20, verbose_name='Tipo de Evento')),
                ('fecha_evento', models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Evento')),
                ('motivo_devolucion', models.TextField(blank=True, null=True, verbose_name='Motivo de Devolución')),
                ('fecha_entrada_subestado', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Entrada al Subestado')),
                ('fecha_salida_subestado', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Salida del Subestado')),
                ('tiempo_en_subestado', models.DurationField(blank=True, null=True, verbose_name='Tiempo en Subestado')),
                ('documento_nombre', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nombre del Documento')),
                ('calificacion_anterior', models.CharField(blank=True, max_length=20, null=True, verbose_name='Calificación Anterior')),
                ('calificacion_nueva', models.CharField(blank=True, max_length=20, null=True, verbose_name='Calificación Nueva')),
                ('requisito_solicitud_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='ID del Requisito de Solicitud')),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones Adicionales')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_backoffice', to='workflow.solicitud', verbose_name='Solicitud')),
                ('subestado_destino', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='historial_como_destino', to='workflow.subestado', verbose_name='Subestado Destino')),
                ('subestado_origen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='historial_como_origen', to='workflow.subestado', verbose_name='Subestado Origen')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario Responsable')),
            ],
            options={
                'verbose_name': 'Historial Back Office',
                'verbose_name_plural': 'Historial Back Office',
                'db_table': 'workflow_historial_backoffice',
                'ordering': ['-fecha_evento'],
                'indexes': [
                    models.Index(fields=['solicitud', 'tipo_evento'], name='workflow_hi_solicit_e326f5_idx'), 
                    models.Index(fields=['fecha_evento'], name='workflow_hi_fecha_e_458661_idx'), 
                    models.Index(fields=['usuario'], name='workflow_hi_usuario_eb9f54_idx')
                ],
            },
        ),
    ]