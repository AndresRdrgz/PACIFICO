# Generated manually - Database agnostic migration for ClienteEntrevista
# This migration creates the table if it doesn't exist using database-specific syntax

from django.db import migrations, models
import django.db.models.deletion


def create_table_if_not_exists_postgresql(apps, schema_editor):
    """Create ClienteEntrevista table if it doesn't exist - Multi-database compatible"""
    from django.db import connection
    
    # Detectar el tipo de base de datos
    if 'postgresql' in connection.settings_dict['ENGINE']:
        # PostgreSQL - usar information_schema
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'workflow_clienteentrevista'
                );
            """)
            table_exists = cursor.fetchone()[0]
    elif 'sqlite' in connection.settings_dict['ENGINE']:
        # SQLite - usar sqlite_master
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name='workflow_clienteentrevista';
            """)
            table_exists = cursor.fetchone()[0] > 0
    else:
        # Para otras bases de datos, intentar crear la tabla directamente
        table_exists = False
    
    if not table_exists:
        # Create table using Django's schema editor
        ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
        schema_editor.create_model(ClienteEntrevista)
        print("Created workflow_clienteentrevista table")
    else:
        print("Table workflow_clienteentrevista already exists")


def reverse_create_table_postgresql(apps, schema_editor):
    """Reverse the table creation - Multi-database compatible"""
    from django.db import connection
    
    # Detectar el tipo de base de datos para el comando DROP
    if 'postgresql' in connection.settings_dict['ENGINE']:
        # PostgreSQL - usar CASCADE
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista CASCADE")
    elif 'sqlite' in connection.settings_dict['ENGINE']:
        # SQLite - sin CASCADE
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista")
    else:
        # Para otras bases de datos, usar Django's schema editor
        try:
            ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
            schema_editor.delete_model(ClienteEntrevista)
        except:
            # Si falla, intentar DROP básico
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        migrations.RunPython(
            create_table_if_not_exists_postgresql,
            reverse_create_table_postgresql,
        ),
    ]
