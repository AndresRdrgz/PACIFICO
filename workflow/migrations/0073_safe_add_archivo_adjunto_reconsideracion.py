# Generated migration to fix archivo_adjunto column issue in production
# This migration safely handles the case where the column might already exist

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
            print("✅ Column archivo_adjunto already exists in workflow_reconsideracionsolicitud - skipping")


def remove_archivo_adjunto_field_safe(apps, schema_editor):
    """Remove archivo_adjunto field safely, checking if it exists."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if the column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'workflow_reconsideracionsolicitud' 
            AND column_name = 'archivo_adjunto'
        """)
        
        if cursor.fetchone():
            # Column exists, remove it
            cursor.execute("""
                ALTER TABLE workflow_reconsideracionsolicitud 
                DROP COLUMN archivo_adjunto
            """)
            print("✅ Removed archivo_adjunto column from workflow_reconsideracionsolicitud")
        else:
            print("✅ Column archivo_adjunto doesn't exist in workflow_reconsideracionsolicitud - skipping")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0072_delete_reconsideracionpdf'),
    ]

    operations = [
        migrations.RunPython(
            add_archivo_adjunto_field_safe,
            remove_archivo_adjunto_field_safe
        ),
    ]
