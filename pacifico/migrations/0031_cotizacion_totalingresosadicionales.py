# Generated by Django 5.1.3 on 2024-12-11 14:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0030_cotizacion_abonoporcentaje"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="totalIngresosAdicionales",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
