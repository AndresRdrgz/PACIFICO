# Generated by Django 5.1.3 on 2024-12-27 16:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0061_cliente_primermes_cliente_tipoprorrateo_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cliente",
            name="primerMes",
            field=models.CharField(
                choices=[
                    ("ENERO", "ENERO"),
                    ("FEBRERO", "FEBRERO"),
                    ("MARZO", "MARZO"),
                    ("ABRIL", "ABRIL"),
                    ("MAYO", "MAYO"),
                    ("JUNIO", "JUNIO"),
                    ("JULIO", "JULIO"),
                    ("AGOSTO", "AGOSTO"),
                    ("SEPTIEMBRE", "SEPTIEMBRE"),
                    ("OCTUBRE", "OCTUBRE"),
                    ("NOVIEMBRE", "NOVIEMBRE"),
                    ("DICIEMBRE", "DICIEMBRE"),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="cotizacion",
            name="primerMes",
            field=models.CharField(
                choices=[
                    ("ENERO", "ENERO"),
                    ("FEBRERO", "FEBRERO"),
                    ("MARZO", "MARZO"),
                    ("ABRIL", "ABRIL"),
                    ("MAYO", "MAYO"),
                    ("JUNIO", "JUNIO"),
                    ("JULIO", "JULIO"),
                    ("AGOSTO", "AGOSTO"),
                    ("SEPTIEMBRE", "SEPTIEMBRE"),
                    ("OCTUBRE", "OCTUBRE"),
                    ("NOVIEMBRE", "NOVIEMBRE"),
                    ("DICIEMBRE", "DICIEMBRE"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
