# Generated by Django 5.1.3 on 2024-12-24 20:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0046_cotizacion_wrkletraseguro"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="wrkLetraSinSeguros",
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
