# Generated by Django 5.1.3 on 2024-12-19 20:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0042_cotizacion_calccomicierrefinal_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="manejo_5porc",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
