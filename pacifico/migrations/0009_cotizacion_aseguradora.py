# Generated by Django 5.1.3 on 2024-12-02 17:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0008_aseguradora"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="aseguradora",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="pacifico.aseguradora",
            ),
        ),
    ]
