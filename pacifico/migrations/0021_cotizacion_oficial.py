# Generated by Django 5.1.3 on 2024-12-05 03:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacifico", "0020_cotizacion_cartera_cotizacion_ingresos_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="oficial",
            field=models.CharField(
                choices=[
                    ("AMARELIS ALTAMIRANDA", "AMARELIS ALTAMIRANDA"),
                    ("ANA TERESA BENITEZ", "ANA TERESA BENITEZ"),
                    ("ARGELIS GÓMEZ", "ARGELIS GÓMEZ"),
                    ("BLANCA VERGARA", "BLANCA VERGARA"),
                    ("CHARLEENE CARRERA", "CHARLEENE CARRERA"),
                    ("CHRISTELL GARCIA", "CHRISTELL GARCIA"),
                    ("DEYDA SALDAÑA", "DEYDA SALDAÑA"),
                    ("EILEEN ORTEGA", "EILEEN ORTEGA"),
                    ("ELINA DÍAZ", "ELINA DÍAZ"),
                    ("GLENDA QUINTERO", "GLENDA QUINTERO"),
                    ("ILSA JIMÉNEZ", "ILSA JIMÉNEZ"),
                    ("INISHELL MOSQUERA", "INISHELL MOSQUERA"),
                    ("ISIS BARRIA", "ISIS BARRIA"),
                    ("JEMIMA CASTILLO", "JEMIMA CASTILLO"),
                    ("KENIA SIERRA", "KENIA SIERRA"),
                    ("KRISTY KING", "KRISTY KING"),
                    ("LARISSA MARCIAGA", "LARISSA MARCIAGA"),
                    ("LISETH DEL CARMEN ZAPATA", "LISETH DEL CARMEN ZAPATA"),
                    ("MARICRUZ ARMUELLES", "MARICRUZ ARMUELLES"),
                    ("MELISSA VEGA", "MELISSA VEGA"),
                    ("MIGDALIA TEJEIRA", "MIGDALIA TEJEIRA"),
                    ("ROSEMERY ANDRADE", "ROSEMERY ANDRADE"),
                    ("SHARLEN SAMANIEGO", "SHARLEN SAMANIEGO"),
                    ("STEPHANY SANDOVAL", "STEPHANY SANDOVAL"),
                    ("TAIRA DE OBALDIA", "TAIRA DE OBALDIA"),
                    ("YAJANIS CONCEPCIÓN", "YAJANIS CONCEPCIÓN"),
                    ("YARINETH SANCHEZ", "YARINETH SANCHEZ"),
                    ("YARISBETH ARDINES", "YARISBETH ARDINES"),
                    ("YARKELIS REYES", "YARKELIS REYES"),
                    ("YASHEIKA HENRIQUEZ", "YASHEIKA HENRIQUEZ"),
                    ("YEISHA VILLAMIL", "YEISHA VILLAMIL"),
                    ("YEZKA AVILA", "YEZKA AVILA"),
                    ("YITZEL LÓPEZ", "YITZEL LÓPEZ"),
                    ("YULEISIS GONZÁLEZ", "YULEISIS GONZÁLEZ"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
