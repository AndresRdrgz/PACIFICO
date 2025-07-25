# Generated by Django 5.1.3 on 2025-07-25 06:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0034_add_formulario_general_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solicitud',
            name='formulario_general',
        ),
        migrations.RemoveField(
            model_name='solicitud',
            name='formulario_general_fecha_asociacion',
        ),
        migrations.AddField(
            model_name='solicitud',
            name='entrevista_cliente',
            field=models.ForeignKey(blank=True, help_text='Entrevista de cliente asociada a esta solicitud', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solicitudes', to='workflow.clienteentrevista'),
        ),
    ]
