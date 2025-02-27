# Generated by Django 5.1.3 on 2025-01-07 16:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0076_cotizacion_aplicacodeudor"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="cobonosDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cobonosMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtros1",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtros2",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtros3",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtros4",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosDcto1",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosDcto2",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosDcto3",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosDcto4",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosMonto1",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosMonto2",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosMonto3",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="codirOtrosMonto4",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cohorasExtrasDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cohorasExtrasMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cootrosDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cootrosMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntario1",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntario2",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntario3",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntario4",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntario5",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntario6",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioDcto1",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioDcto2",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioDcto3",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioDcto4",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioDcto5",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioDcto6",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioMonto1",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioMonto2",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioMonto3",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioMonto4",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioMonto5",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copagoVoluntarioMonto6",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copraaDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="copraaMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="coprimaDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="coprimaMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cosiacapDcto",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="cosiacapMonto",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
