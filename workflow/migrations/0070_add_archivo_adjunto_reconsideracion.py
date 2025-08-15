# Generated migration for adding archivo_adjunto field to ReconsideracionSolicitud
# NOTE: This migration does nothing because the field is already handled by migration 0046

from django.db import migrations


def noop_forward(apps, schema_editor):
    """No operation - field already handled by migration 0046"""
    print("✅ Migration 0070: archivo_adjunto field already handled by migration 0046")


def noop_reverse(apps, schema_editor):
    """No operation on reverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0069_reconsideracionpdf'),  # Last existing migration
    ]

    operations = [
        migrations.RunPython(
            noop_forward,
            noop_reverse
        ),
    ]
