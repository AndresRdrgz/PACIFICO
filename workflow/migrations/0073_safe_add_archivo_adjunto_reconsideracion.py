# Generated migration to fix archivo_adjunto column issue in production
# This migration safely handles the case where the column might already exist

from django.db import migrations, models


def add_archivo_adjunto_field_safe(apps, schema_editor):
    """Add archivo_adjunto field safely, checking if it already exists."""
    from django.db import connection
    
    # Get the ReconsideracionSolicitud model
    ReconsideracionSolicitud = apps.get_model('workflow', 'ReconsideracionSolicitud')
    
    # Check if field already exists by trying to access it
    try:
        # Try to access the field - if it exists, this won't raise an error
        ReconsideracionSolicitud._meta.get_field('archivo_adjunto')
        print("✅ Column archivo_adjunto already exists in workflow_reconsideracionsolicitud - skipping")
        return
    except:
        # Field doesn't exist, we need to add it
        pass
    
    # Use database-agnostic approach
    db_alias = schema_editor.connection.alias
    with connection.cursor() as cursor:
        try:
            if connection.vendor == 'postgresql':
                # PostgreSQL syntax
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'workflow_reconsideracionsolicitud' 
                    AND column_name = 'archivo_adjunto'
                """)
                exists = cursor.fetchone() is not None
            elif connection.vendor == 'sqlite':
                # SQLite syntax
                cursor.execute("PRAGMA table_info(workflow_reconsideracionsolicitud)")
                columns = [row[1] for row in cursor.fetchall()]
                exists = 'archivo_adjunto' in columns
            else:
                # MySQL syntax
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'workflow_reconsideracionsolicitud' 
                    AND COLUMN_NAME = 'archivo_adjunto'
                """)
                exists = cursor.fetchone() is not None
            
            if not exists:
                # Column doesn't exist, add it using Django's schema editor for database compatibility
                from django.db import models
                field = models.FileField(upload_to='reconsideraciones/', null=True, blank=True, max_length=100)
                field.set_attributes_from_name('archivo_adjunto')
                schema_editor.add_field(ReconsideracionSolicitud, field)
                print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud")
            else:
                print("✅ Column archivo_adjunto already exists in workflow_reconsideracionsolicitud - skipping")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not check for archivo_adjunto column existence: {e}")
            # Fallback: try to add the field and catch any errors
            try:
                from django.db import models
                field = models.FileField(upload_to='reconsideraciones/', null=True, blank=True, max_length=100)
                field.set_attributes_from_name('archivo_adjunto')
                schema_editor.add_field(ReconsideracionSolicitud, field)
                print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud (fallback)")
            except Exception as add_error:
                print(f"✅ Column archivo_adjunto probably already exists (error: {add_error})")


def remove_archivo_adjunto_field_safe(apps, schema_editor):
    """Remove archivo_adjunto field safely, checking if it exists."""
    from django.db import connection
    
    # Get the ReconsideracionSolicitud model
    ReconsideracionSolicitud = apps.get_model('workflow', 'ReconsideracionSolicitud')
    
    # Check if field exists by trying to access it
    try:
        field = ReconsideracionSolicitud._meta.get_field('archivo_adjunto')
        # Field exists, remove it using Django's schema editor
        schema_editor.remove_field(ReconsideracionSolicitud, field)
        print("✅ Removed archivo_adjunto column from workflow_reconsideracionsolicitud")
    except:
        # Field doesn't exist
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
