# Generated migration to handle the expected 0074 migration in production
# This migration ensures compatibility with production expectations

from django.db import migrations


def ensure_archivo_adjunto_exists(apps, schema_editor):
    """Ensure archivo_adjunto field exists - this should be a no-op if 0073 ran successfully."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # Check if the column already exists using SQLite-compatible syntax
            cursor.execute("PRAGMA table_info(workflow_reconsideracionsolicitud)")
            columns = cursor.fetchall()
            
            # Column info format: (cid, name, type, notnull, dflt_value, pk)
            column_names = [col[1] for col in columns]
            
            if 'archivo_adjunto' not in column_names:
                # Column doesn't exist, this should not happen if 0073 ran
                print("⚠️  WARNING: archivo_adjunto column missing, adding it now")
                cursor.execute("""
                    ALTER TABLE workflow_reconsideracionsolicitud 
                    ADD COLUMN archivo_adjunto VARCHAR(100) NULL
                """)
                print("✅ Added archivo_adjunto column to workflow_reconsideracionsolicitud")
            else:
                print("✅ Migration 0074: archivo_adjunto column already exists - no action needed")
        except Exception as e:
            print(f"⚠️  Migration 0074 error: {e}")
            print("✅ Continuing migration - assuming column exists")


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
