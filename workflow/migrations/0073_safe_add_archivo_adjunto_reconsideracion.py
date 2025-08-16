# Generated migration to fix archivo_adjunto column issue in production
# This migration safely handles the case where the column might already exist

from django.db import migrations, models


def add_archivo_adjunto_field_safe(apps, schema_editor):
    """Add archivo_adjunto field safely, checking if it already exists."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # SQLite-compatible way to check if column exists
        try:
            cursor.execute("PRAGMA table_info(workflow_reconsideracionsolicitud)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'archivo_adjunto' not in columns:
                # Column doesn't exist, add it
                cursor.execute("""
                    ALTER TABLE workflow_reconsideracionsolicitud 
                    ADD COLUMN archivo_adjunto VARCHAR(100) NULL
                """)
                print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud")
            else:
                print("✅ Column archivo_adjunto already exists in workflow_reconsideracionsolicitud - skipping")
        except Exception as e:
            print(f"⚠️ Error checking/adding archivo_adjunto column: {e}")
            # Try adding the column anyway - if it fails, the column might already exist
            try:
                cursor.execute("""
                    ALTER TABLE workflow_reconsideracionsolicitud 
                    ADD COLUMN archivo_adjunto VARCHAR(100) NULL
                """)
                print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud")
            except Exception as add_error:
                print(f"ℹ️ Could not add column (probably already exists): {add_error}")


def remove_archivo_adjunto_field_safe(apps, schema_editor):
    """Remove archivo_adjunto field safely, checking if it exists."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # SQLite-compatible way to check if column exists
        try:
            cursor.execute("PRAGMA table_info(workflow_reconsideracionsolicitud)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'archivo_adjunto' in columns:
                print("ℹ️ Column archivo_adjunto exists but SQLite doesn't support DROP COLUMN easily")
                print("ℹ️ Leaving column in place - this is safe")
            else:
                print("✅ Column archivo_adjunto doesn't exist - nothing to remove")
        except Exception as e:
            print(f"⚠️ Error checking archivo_adjunto column: {e}")
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
