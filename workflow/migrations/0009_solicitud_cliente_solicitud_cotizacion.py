# Generated by Django 5.1.3 on 2025-07-07 17:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacifico', '0146_remove_cotizacion_etiquetas_oficial_and_more'),
        ('workflow', '0008_alter_solicitud_prioridad'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes', to='pacifico.cliente'),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='cotizacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes', to='pacifico.cotizacion'),
        ),
    ]
