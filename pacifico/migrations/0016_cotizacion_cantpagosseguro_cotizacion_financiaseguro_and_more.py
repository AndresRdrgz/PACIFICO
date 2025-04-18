# Generated by Django 5.1.3 on 2024-12-03 17:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0015_cotizacion_vendedor_cotizacion_vendedorcomision_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="cantPagosSeguro",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="financiaSeguro",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="mesesFinanciaSeguro",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="montoMensualSeguro",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="montoanualSeguro",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
