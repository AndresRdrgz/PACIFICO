# Generated manually - Database agnostic migration for ClienteEntrevista
# This migration creates the table if it doesn't exist using database-specific syntax

from django.db import migrations, models
import django.db.models.deletion


def create_table_if_not_exists_database_agnostic(apps, schema_editor):
    """Create ClienteEntrevista table if it doesn't exist - Database agnostic"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if table exists (database agnostic approach)
        db_engine = connection.vendor
        
        if db_engine == 'postgresql':
            # PostgreSQL specific query
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'workflow_clienteentrevista'
                );
            """)
        elif db_engine == 'sqlite':
            # SQLite specific query
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='workflow_clienteentrevista';
            """)
        elif db_engine == 'mysql':
            # MySQL specific query
            cursor.execute("""
                SELECT TABLE_NAME FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'workflow_clienteentrevista';
            """)
        else:
            # Fallback - try to query the table directly
            try:
                cursor.execute("SELECT 1 FROM workflow_clienteentrevista LIMIT 1;")
                table_exists = True
            except:
                table_exists = False
        
        if db_engine == 'postgresql':
            result = cursor.fetchone()
            table_exists = result[0] if result else False
        elif db_engine in ['sqlite', 'mysql']:
            result = cursor.fetchone()
            table_exists = bool(result)
        # table_exists is already set for the fallback case
        
        if not table_exists:
            # Create table using Django's schema editor
            ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
            schema_editor.create_model(ClienteEntrevista)
            print("Created workflow_clienteentrevista table")
        else:
            print("Table workflow_clienteentrevista already exists")


def reverse_create_table_database_agnostic(apps, schema_editor):
    """Reverse the table creation - Database agnostic"""
    from django.db import connection
    
    db_engine = connection.vendor
    with connection.cursor() as cursor:
        if db_engine == 'postgresql':
            cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista CASCADE")
        elif db_engine == 'sqlite':
            cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista")
        elif db_engine == 'mysql':
            cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista")
        else:
            # Fallback
            try:
                cursor.execute("DROP TABLE workflow_clienteentrevista")
            except:
                pass  # Table might not exist


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        migrations.RunPython(
            create_table_if_not_exists_database_agnostic,
            reverse_create_table_database_agnostic,
        ),
    ]
