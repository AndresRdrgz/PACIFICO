# Generated by Django 5.1.3 on 2025-07-06 01:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capacitaciones_app', '0021_curso_tipo_curso'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='grupoasignacion',
            name='supervisor',
            field=models.ForeignKey(blank=True, limit_choices_to={'userprofile__rol': 'Supervisor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grupos_supervisados', to=settings.AUTH_USER_MODEL),
        ),
    ]
