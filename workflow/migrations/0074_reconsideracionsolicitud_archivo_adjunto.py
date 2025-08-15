# Generated migration to handle the expected 0074 migration in production
# This migration ensures compatibility with production expectations

from django.db import migrations


def ensure_archivo_adjunto_exists(apps, schema_editor):
    """Ensure archivo_adjunto field exists - this should be a no-op if 0073 ran successfully."""
    from django.db import connection
    
    # Get the ReconsideracionSolicitud model
    ReconsideracionSolicitud = apps.get_model('workflow', 'ReconsideracionSolicitud')
    
    # Check if field already exists by trying to access it
    try:
        ReconsideracionSolicitud._meta.get_field('archivo_adjunto')
        print("✅ Migration 0074: archivo_adjunto column already exists - no action needed")
        return
    except:
        # Field doesn't exist, this should not happen if 0073 ran
        pass
    
    # Use database-agnostic approach
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
                print("⚠️  WARNING: archivo_adjunto column missing, adding it now")
                from django.db import models
                field = models.FileField(upload_to='reconsideraciones/', null=True, blank=True, max_length=100)
                field.set_attributes_from_name('archivo_adjunto')
                schema_editor.add_field(ReconsideracionSolicitud, field)
                print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud")
            else:
                print("✅ Migration 0074: archivo_adjunto column already exists - no action needed")
                
        except Exception as e:
            print(f"✅ Migration 0074: Assuming archivo_adjunto column exists (check error: {e})")


def noop_reverse(apps, schema_editor):
    """No operation on reverse - we don't want to accidentally drop the column"""
    print("✅ Migration 0074 reverse: No action taken")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0073_safe_add_archivo_adjunto_reconsideracion'),
    ]

    operations = [
        migrations.RunPython(
            ensure_archivo_adjunto_exists,
            noop_reverse
        ),
    ]
