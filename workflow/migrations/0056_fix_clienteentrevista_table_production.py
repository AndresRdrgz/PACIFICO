# Generated manually to fix ClienteEntrevista table in production
# This migration handles the case where the table might be missing or incomplete

from django.db import migrations, models, connection, transaction
from django.db.utils import ProgrammingError


def fix_clienteentrevista_table(apps, schema_editor):
    """Fix ClienteEntrevista table if it's missing or incomplete."""
    table_name = 'workflow_clienteentrevista'
    
    # Check if table exists and has required structure
    table_exists = False
    table_has_correct_structure = False
    
    # Use separate transaction to check table existence
    with transaction.atomic():
        try:
            with connection.cursor() as cursor:
                # Check if table exists using SQLite-compatible syntax
                try:
                    cursor.execute("PRAGMA table_info(%s)" % table_name)
                    columns = cursor.fetchall()
                    table_exists = len(columns) > 0
                except Exception:
                    # Fallback: try to select from the table
                    try:
                        cursor.execute("SELECT * FROM %s LIMIT 1" % table_name)
                        table_exists = True
                    except Exception:
                        table_exists = False
        except Exception as e:
            print(f"Error checking table existence: {e}")
            table_exists = False
    
    if table_exists:
        # Check if table has the expected structure
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT primer_nombre FROM {table_name} LIMIT 1")
                table_has_correct_structure = True
                print(f"✅ Table {table_name} exists with correct structure")
                return
            except Exception as e:
                print(f"❌ Table {table_name} exists but has incorrect structure: {e}")
                table_has_correct_structure = False
    
    # If we get here, table either doesn't exist or has wrong structure
    if table_exists and not table_has_correct_structure:
        # Drop and recreate table
        print(f"🔧 Dropping and recreating table {table_name}...")
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"✅ Dropped existing table {table_name}")
            except Exception as e:
                print(f"Error dropping table: {e}")
    else:
        print(f"🔧 Table {table_name} does not exist - creating...")
    
    # Create the table with correct structure
    try:
        ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
        schema_editor.create_model(ClienteEntrevista)
        print(f"✅ Created table {table_name} with correct structure")
    except Exception as e:
        print(f"Error creating table: {e}")
        # If table already exists, just log it and continue
        if "already exists" in str(e):
            print(f"ℹ️  Table {table_name} already exists - skipping creation")
            return
        raise


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
