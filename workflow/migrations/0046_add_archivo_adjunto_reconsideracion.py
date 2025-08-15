# Generated migration for adding archivo_adjunto field to ReconsideracionSolicitud

from django.db import migrations, models


def add_archivo_adjunto_field_safe(apps, schema_editor):
    """Add archivo_adjunto field safely, checking if it already exists."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if the column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'workflow_reconsideracionsolicitud' 
            AND column_name = 'archivo_adjunto'
        """)
        
        if not cursor.fetchone():
            # Column doesn't exist, add it
            cursor.execute("""
                ALTER TABLE workflow_reconsideracionsolicitud 
                ADD COLUMN archivo_adjunto VARCHAR(100) NULL
            """)
            print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud")
        else:
            print("✅ Column archivo_adjunto already exists in workflow_reconsideracionsolicitud")


def remove_archivo_adjunto_field(apps, schema_editor):
    """Remove archivo_adjunto field if it exists."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'workflow_reconsideracionsolicitud' 
            AND column_name = 'archivo_adjunto'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE workflow_reconsideracionsolicitud 
                DROP COLUMN archivo_adjunto
            """)
            print("✅ Removed archivo_adjunto column from workflow_reconsideracionsolicitud")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0045_add_orden_seccion_field'),  # Updated to actual last migration
    ]

    operations = [
        migrations.RunPython(
            add_archivo_adjunto_field_safe,
            remove_archivo_adjunto_field
        ),
    ]
