# Generated by Django 5.1.3 on 2024-12-02 16:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0003_cotizacion_comicierre_cotizacion_fechainiciopago_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="montoPrestamo",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
