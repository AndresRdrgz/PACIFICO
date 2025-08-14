# Generated manually - SQLite compatible migration for ClienteEntrevista
# This migration creates the table if it doesn't exist using SQLite syntax

from django.db import migrations, models
import django.db.models.deletion


def create_table_if_not_exists_sqlite(apps, schema_editor):
    """Create ClienteEntrevista table if it doesn't exist - SQLite compatible"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if table exists (SQLite compatible)
        try:
            cursor.execute("PRAGMA table_info(workflow_clienteentrevista)")
            table_exists = len(cursor.fetchall()) > 0
        except Exception:
            # Fallback: try to select from the table
            try:
                cursor.execute("SELECT * FROM workflow_clienteentrevista LIMIT 1")
                table_exists = True
            except Exception:
                table_exists = False
        
        if not table_exists:
            # Create table using Django's schema editor
            ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
            schema_editor.create_model(ClienteEntrevista)
            print("Created workflow_clienteentrevista table")
        else:
            print("Table workflow_clienteentrevista already exists")


def reverse_create_table_sqlite(apps, schema_editor):
    """Reverse the table creation - SQLite compatible"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        migrations.RunPython(
            create_table_if_not_exists_sqlite,
            reverse_create_table_sqlite,
        ),
    ]
