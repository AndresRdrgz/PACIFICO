# Generated manually - Simple safe migration for ClienteEntrevista
# This migration is a backup in case the complex one fails

from django.db import migrations


def noop_operation(apps, schema_editor):
    """No-op operation that does nothing - safe fallback"""
    print("ℹ️  Emergency no-op migration for ClienteEntrevista - no action taken")


def reverse_noop_operation(apps, schema_editor):
    """Reverse no-op operation - also does nothing"""
    print("ℹ️  Reverse emergency no-op migration - no action taken")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        # This is a minimal no-op migration to replace the problematic ones
        # The actual table should be created manually using the emergency script
        migrations.RunPython(
            noop_operation,
            reverse_noop_operation,
        ),
    ]
