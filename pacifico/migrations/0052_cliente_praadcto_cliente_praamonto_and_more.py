# Generated by Django 5.1.3 on 2024-12-26 19:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0051_cliente_cartera_cliente_ingresos_cliente_licencia_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="praaDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cliente",
            name="praaMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="siacapDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cliente",
            name="siacapMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="praaDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="praaMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="siacapDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="siacapMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]