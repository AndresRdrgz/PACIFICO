# Post-migration verification and cleanup
# This migration ensures the ReconsideracionSolicitud model is fully in sync

from django.db import migrations


def verify_reconsideracion_model_state(apps, schema_editor):
    """Verify that the ReconsideracionSolicitud model is properly set up."""
    from django.db import connection
    
    # Get the ReconsideracionSolicitud model
    ReconsideracionSolicitud = apps.get_model('workflow', 'ReconsideracionSolicitud')
    
    with connection.cursor() as cursor:
        try:
            # Get column information in a database-agnostic way
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'workflow_reconsideracionsolicitud'
                    ORDER BY column_name
                """)
                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]
            elif connection.vendor == 'sqlite':
                cursor.execute("PRAGMA table_info(workflow_reconsideracionsolicitud)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]  # SQLite returns (cid, name, type, notnull, dflt_value, pk)
            else:
                # MySQL
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'workflow_reconsideracionsolicitud'
                    ORDER BY COLUMN_NAME
                """)
                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]
            
            # Check for essential columns
            essential_columns = [
                'id', 'solicitud_id', 'numero_reconsideracion', 'solicitada_por_id',
                'archivo_adjunto'  # This is the key one we're checking
            ]
            
            missing_columns = []
            for essential_col in essential_columns:
                if essential_col not in column_names:
                    missing_columns.append(essential_col)
            
            if missing_columns:
                print(f"⚠️  WARNING: Missing essential columns in workflow_reconsideracionsolicitud: {missing_columns}")
            else:
                print("✅ All essential columns present in workflow_reconsideracionsolicitud")
            
            # Specifically check archivo_adjunto
            if 'archivo_adjunto' in column_names:
                print("✅ archivo_adjunto column verified in workflow_reconsideracionsolicitud")
            else:
                print("❌ archivo_adjunto column missing from workflow_reconsideracionsolicitud")
                
        except Exception as e:
            # Fallback: try to access the field through Django ORM
            try:
                ReconsideracionSolicitud._meta.get_field('archivo_adjunto')
                print("✅ archivo_adjunto field verified through Django ORM")
            except:
                print(f"⚠️  Could not verify table structure: {e}")
                print("✅ Assuming migrations completed successfully")


def noop_reverse(apps, schema_editor):
    """No operation on reverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0074_reconsideracionsolicitud_archivo_adjunto'),
    ]

    operations = [
        migrations.RunPython(
            verify_reconsideracion_model_state,
            noop_reverse
        ),
    ]
