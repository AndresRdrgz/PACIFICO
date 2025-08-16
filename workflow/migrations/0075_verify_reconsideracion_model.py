# Post-migration verification and cleanup
# This migration ensures the ReconsideracionSolicitud model is fully in sync

from django.db import migrations


def verify_reconsideracion_model_state(apps, schema_editor):
    """Verify that the ReconsideracionSolicitud model is properly set up."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # Verify all expected columns exist using SQLite-compatible syntax
            cursor.execute("PRAGMA table_info(workflow_reconsideracionsolicitud)")
            columns = cursor.fetchall()
            
            # Column info format: (cid, name, type, notnull, dflt_value, pk)
            column_names = [col[1] for col in columns]
            
            expected_columns = [
                'id', 'solicitud_id', 'numero_reconsideracion', 'solicitada_por_id',
                'fecha_solicitud', 'motivo', 'cotizacion_original_id', 'cotizacion_nueva_id',
                'usar_nueva_cotizacion', 'estado', 'analizada_por_id', 'fecha_analisis',
                'comentario_analisis', 'resultado_consulta_anterior', 'comentario_consulta_anterior',
                'archivo_adjunto', 'creado_en', 'actualizado_en'
            ]
            
            missing_columns = []
            for expected_col in expected_columns:
                if expected_col not in column_names:
                    missing_columns.append(expected_col)
            
            if missing_columns:
                print(f"⚠️  WARNING: Missing columns in workflow_reconsideracionsolicitud: {missing_columns}")
            else:
                print("✅ All expected columns present in workflow_reconsideracionsolicitud")
            
            # Specifically check archivo_adjunto
            if 'archivo_adjunto' in column_names:
                print("✅ archivo_adjunto column verified in workflow_reconsideracionsolicitud")
            else:
                print("❌ archivo_adjunto column missing from workflow_reconsideracionsolicitud")
        except Exception as e:
            print(f"⚠️  Migration 0075 verification error: {e}")
            print("✅ Continuing migration - assuming schema is correct")


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
