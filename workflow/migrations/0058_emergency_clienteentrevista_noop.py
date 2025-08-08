# Generated manually - Simple safe migration for ClienteEntrevista
# This migration is a backup in case the complex one fails

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        # This is a minimal no-op migration to replace the problematic ones
        # The actual table should be created manually using the emergency script
        migrations.RunSQL(
            sql="SELECT 1 WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'workflow_clienteentrevista');",
            reverse_sql="SELECT 1;",
        ),
    ]
