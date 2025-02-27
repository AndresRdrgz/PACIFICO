# Generated by Django 5.1.3 on 2024-12-02 17:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0009_cotizacion_aseguradora"),
    ]

    operations = [
        migrations.CreateModel(
            name="FormPago",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("descripcion", models.CharField(max_length=100, null=True)),
                ("codigo", models.IntegerField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="formaPago",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="pacifico.formpago",
            ),
        ),
    ]
