# Generated by Django 5.1.3 on 2025-06-17 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mantenimiento', '0005_remove_promocion_tipo_vendedor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocion',
            name='producto',
            field=models.CharField(choices=[('PREST AUTO', 'Prest. Auto'), ('PERSONAL', 'Personal')], max_length=20),
        ),
    ]
