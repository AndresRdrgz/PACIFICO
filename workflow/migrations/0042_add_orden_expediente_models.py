# Generated manually - Orden de Expediente models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0041_add_subsanado_to_calificacion_documento_backoffice'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdenExpediente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seccion', models.CharField(help_text='Sección del expediente (ej: Documentos Personales)', max_length=200)),
                ('nombre_documento', models.CharField(help_text='Nombre del documento', max_length=300)),
                ('orden', models.PositiveIntegerField(help_text='Orden del documento dentro de su sección')),
                ('tiene_documento', models.BooleanField(default=False, help_text='Indica si el documento está presente')),
                ('obligatorio', models.BooleanField(default=True, help_text='Indica si el documento es obligatorio')),
                ('fecha_calificacion', models.DateTimeField(blank=True, help_text='Fecha de última calificación', null=True)),
                ('comentarios', models.TextField(blank=True, help_text='Comentarios sobre el documento', null=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True, help_text='Si está inactivo, no se muestra en la interfaz')),
                ('calificado_por', models.ForeignKey(blank=True, help_text='Usuario que calificó este documento', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documentos_calificados', to=settings.AUTH_USER_MODEL)),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orden_expediente', to='workflow.solicitud')),
            ],
            options={
                'verbose_name': 'Orden de Expediente',
                'verbose_name_plural': 'Orden de Expedientes',
                'ordering': ['seccion', 'orden', 'nombre_documento'],
                'unique_together': {('solicitud', 'seccion', 'orden')},
            },
        ),
        migrations.CreateModel(
            name='PlantillaOrdenExpediente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seccion', models.CharField(help_text='Sección del expediente', max_length=200)),
                ('nombre_documento', models.CharField(help_text='Nombre del documento', max_length=300)),
                ('orden', models.PositiveIntegerField(help_text='Orden del documento dentro de su sección')),
                ('obligatorio', models.BooleanField(default=True, help_text='Indica si el documento es obligatorio')),
                ('descripcion', models.TextField(blank=True, help_text='Descripción adicional del documento', null=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True, help_text='Si está inactivo, no se aplica a nuevas solicitudes')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plantillas_creadas', to=settings.AUTH_USER_MODEL)),
                ('pipeline', models.ForeignKey(help_text='Pipeline al que aplica esta plantilla', on_delete=django.db.models.deletion.CASCADE, related_name='plantillas_orden', to='workflow.pipeline')),
            ],
            options={
                'verbose_name': 'Plantilla de Orden de Expediente',
                'verbose_name_plural': 'Plantillas de Orden de Expediente',
                'ordering': ['pipeline', 'seccion', 'orden', 'nombre_documento'],
                'unique_together': {('pipeline', 'seccion', 'orden')},
            },
        ),
    ]