# Generated manually to add missing cliente_nombre and cliente_cedula fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0023_remove_formularioweb_oficial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='cliente_nombre',
            field=models.CharField(blank=True, help_text='Nombre completo del cliente', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='solicitud',
            name='cliente_cedula',
            field=models.CharField(blank=True, help_text='Cédula del cliente', max_length=50, null=True),
        ),
    ] 