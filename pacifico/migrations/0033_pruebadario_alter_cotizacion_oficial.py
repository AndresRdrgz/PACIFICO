# Generated by Django 5.1.3 on 2024-12-12 21:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "pacifico",
            "0032_alter_cotizacion_comicierre_alter_cotizacion_oficial_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="PruebaDario",
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
                ("nombre", models.CharField(max_length=100, null=True)),
                ("apellido", models.CharField(max_length=100, null=True)),
                ("departamento", models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name="cotizacion",
            name="oficial",
            field=models.CharField(
                choices=[
                    ("TAIRA DE OBALDIA", "TAIRA DE OBALDIA"),
                    ("GERALDINE RODRIGUEZ", "GERALDINE RODRIGUEZ"),
                    ("BLANCA VERGARA", "BLANCA VERGARA"),
                    ("MICHELLE SANTANA", "MICHELLE SANTANA"),
                    ("SHARLEN SAMANIEGO", "SHARLEN SAMANIEGO"),
                    ("ISIS BARRIA", "ISIS BARRIA"),
                    ("ILSA JIMÉNEZ", "ILSA JIMÉNEZ"),
                    ("MELISSA VEGA", "MELISSA VEGA"),
                    ("ESTEFANI FORD", "ESTEFANI FORD"),
                    ("CHARLEENE CARRERA", "CHARLEENE CARRERA"),
                    ("INISHELL MOSQUERA", "INISHELL MOSQUERA"),
                    ("JEMIMA CASTILLO", "JEMIMA CASTILLO"),
                    ("KENIA SIERRA", "KENIA SIERRA"),
                    ("YARINETH SANCHEZ", "YARINETH SANCHEZ"),
                    ("AMARELIS ALTAMIRANDA", "AMARELIS ALTAMIRANDA"),
                    ("DAVID ARAUZ", "DAVID ARAUZ"),
                    ("KRISTY KING", "KRISTY KING"),
                    ("YAJANIS CONCEPCIÓN", "YAJANIS CONCEPCIÓN"),
                    ("YEZKA AVILA", "YEZKA AVILA"),
                    ("MIGDALIA TEJEIRA", "MIGDALIA TEJEIRA"),
                    ("HANNY CISNEROS", "HANNY CISNEROS"),
                    ("YITZEL LÓPEZ", "YITZEL LÓPEZ"),
                    ("NELLY CAMAÑO", "NELLY CAMAÑO"),
                    ("DEYDA SALDAÑA", "DEYDA SALDAÑA"),
                    ("JAVIER CASTILLO", "JAVIER CASTILLO"),
                    ("ELINA DÍAZ", "ELINA DÍAZ"),
                    ("YARKELIS REYES", "YARKELIS REYES"),
                    ("STEPHANY SANDOVAL", "STEPHANY SANDOVAL"),
                    ("MARICRUZ ARMUELLES", "MARICRUZ ARMUELLES"),
                    ("LARISSA MARCIAGA", "LARISSA MARCIAGA"),
                    ("SHELUNSKA MASA", "SHELUNSKA MASA"),
                    ("ARGELIS GOMEZ", "ARGELIS GOMEZ"),
                    ("ROSMERY ANDRADE", "ROSMERY ANDRADE"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
