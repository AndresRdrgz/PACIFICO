# Generated by Django 5.1.3 on 2025-04-16 22:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tombola", "0013_alter_formulariotombola_producto_interesado"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="formulariotombola",
            name="es_cliente",
        ),
        migrations.RemoveField(
            model_name="formulariotombola",
            name="garantia",
        ),
    ]
