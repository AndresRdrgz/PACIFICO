# Generated manually - Simple emergency migration for ClienteEntrevista
# This migration creates the table if it doesn't exist

from django.db import migrations, models
import django.db.models.deletion


def create_table_if_not_exists(apps, schema_editor):
    """Create ClienteEntrevista table if it doesn't exist"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if table exists (SQLite compatible)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name='workflow_clienteentrevista';
        """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Create table using Django's schema editor
            ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
            schema_editor.create_model(ClienteEntrevista)
            print("Created workflow_clienteentrevista table")
        else:
            print("Table workflow_clienteentrevista already exists")


def reverse_create_table(apps, schema_editor):
    """Reverse the table creation"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        migrations.RunPython(
            create_table_if_not_exists,
            reverse_create_table,
        ),
    ]
