# Generated by Django 5.1.3 on 2025-01-03 17:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0066_cotizacion_kilometrajeauto_cotizacion_nuevoauto_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cotizacion",
            name="tasaInteres",
        ),
    ]