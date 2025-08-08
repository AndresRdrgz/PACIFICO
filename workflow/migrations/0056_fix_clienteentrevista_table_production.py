# Generated manually to fix ClienteEntrevista table in production
# This migration handles the case where the table might be missing or incomplete

from django.db import migrations, models, connection
from django.db.utils import ProgrammingError


def fix_clienteentrevista_table(apps, schema_editor):
    """Fix ClienteEntrevista table if it's missing or incomplete."""
    table_name = 'workflow_clienteentrevista'
    
    try:
        # Try to query the table to see if it exists and has the required columns
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT primer_nombre FROM {table_name} LIMIT 1")
        print(f"✅ Table {table_name} exists with primer_nombre column")
        return
    except ProgrammingError:
        # Table doesn't exist or column is missing
        print(f"❌ Table {table_name} is missing or incomplete")
    
    try:
        # Check if table exists at all
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        # Table exists but missing columns - recreate it
        print(f"🔧 Table {table_name} exists but missing columns - recreating...")
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    except ProgrammingError:
        # Table doesn't exist
        print(f"🔧 Table {table_name} does not exist - creating...")
    
    # Create the table with correct structure
    ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
    schema_editor.create_model(ClienteEntrevista)
    print(f"✅ Created/recreated table {table_name} with correct structure")


def reverse_fix_clienteentrevista_table(apps, schema_editor):
    """Reverse operation - this is a no-op since we're fixing the table."""
    print("ℹ️  Reverse operation for ClienteEntrevista table fix - no action needed")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        migrations.RunPython(
            fix_clienteentrevista_table,
            reverse_fix_clienteentrevista_table,
        ),
    ]
