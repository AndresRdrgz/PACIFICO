# Generated by Django 5.1.3 on 2024-12-04 02:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "pacifico",
            "0016_cotizacion_cantpagosseguro_cotizacion_financiaseguro_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="cotizacion",
            name="cantPagosSeguro",
            field=models.IntegerField(default=12, null=True),
        ),
        migrations.AlterField(
            model_name="cotizacion",
            name="mesesFinanciaSeguro",
            field=models.IntegerField(default=3, null=True),
        ),
    ]
