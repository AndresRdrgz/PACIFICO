# Generated by Django 5.1.3 on 2025-05-18 17:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capacitaciones_app', '0006_curso_usuarios_asignados'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoAsignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('cursos', models.ManyToManyField(related_name='grupos_asignados', to='capacitaciones_app.curso')),
                ('miembros', models.ManyToManyField(related_name='grupos_asignados', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
