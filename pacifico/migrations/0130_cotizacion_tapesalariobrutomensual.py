# Generated by Django 5.1.3 on 2025-05-30 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacifico', '0129_cotizacion_tapesalarionetomensual'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizacion',
            name='tapeSalarioBrutoMensual',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
