# Generated by Django 5.1.3 on 2025-06-16 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacifico', '0134_cotizacion_tapecapacidad50_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='rol',
            field=models.CharField(choices=[('Oficial', 'Oficial'), ('Administrador', 'Administrador'), ('Supervisor', 'Supervisor'), ('Alumno', 'Alumno')], default='Oficial', max_length=20),
        ),
    ]
