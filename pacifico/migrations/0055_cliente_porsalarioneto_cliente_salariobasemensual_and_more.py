# Generated by Django 5.1.3 on 2024-12-26 19:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0054_cliente_pagovoluntario1_cliente_pagovoluntario2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="porSalarioNeto",
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="salarioBaseMensual",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="salarioNeto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="salarioNetoActual",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="totalDescuentoDirecto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="totalDescuentosLegales",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cliente",
            name="totalPagoVoluntario",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="porSalarioNeto",
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="salarioNeto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="salarioNetoActual",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="totalDescuentoDirecto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="totalDescuentosLegales",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="totalPagoVoluntario",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
