# Generated by Django 5.1.3 on 2025-07-21 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0021_solicitud_apc_no_cedula_solicitud_apc_tipo_documento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='apc_fecha_completado',
            field=models.DateTimeField(blank=True, help_text='Fecha cuando se completó el proceso APC', null=True),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='apc_fecha_inicio',
            field=models.DateTimeField(blank=True, help_text='Fecha cuando Makito inició el proceso', null=True),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='apc_fecha_solicitud',
            field=models.DateTimeField(blank=True, help_text='Fecha cuando se solicitó el APC', null=True),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='apc_observaciones',
            field=models.TextField(blank=True, help_text='Observaciones del proceso APC', null=True),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='apc_status',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('in_progress', 'En Proceso'), ('completed', 'Completado'), ('error', 'Error')], default='pending', help_text='Estado del proceso APC con Makito', max_length=20),
        ),
    ]
