# Generated by Django 5.1.3 on 2024-12-06 23:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0029_cotizacion_abono"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="abonoPorcentaje",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=5, null=True
            ),
        ),
    ]
