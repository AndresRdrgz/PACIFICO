# Generated by Django 5.1.3 on 2024-12-06 23:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0028_cotizacion_cashback_alter_cotizacion_referenciasapc"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="abono",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10, null=True
            ),
        ),
    ]
