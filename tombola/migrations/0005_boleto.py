# Generated by Django 5.1.3 on 2025-04-08 22:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tombola', '0004_alter_tombola_fecha_evento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boleto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('tombola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boletos', to='tombola.tombola')),
            ],
            options={
                'db_table': 'boleto',
            },
        ),
    ]
