"""
Django management command to fix duplicate analyst comments
"""

import os
import sys
import django

# Add project root to path
project_root = '/Users/andresrdrgz_/Documents/GitHub/PACIFICO'
sys.path.append(project_root)
os.chdir(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')

try:
    import django
    django.setup()
    
    from workflow.modelsWorkflow import Solicitud, CalificacionCampo
    from django.db import transaction
    from django.utils import timezone
    
    def main():
        print("CLEANING UP DUPLICATE ANALYST COMMENTS")
        print("="*50)
        
        solicitud_codigo = "FLU-132"
        
        try:
            solicitud = Solicitud.objects.get(codigo=solicitud_codigo)
            print(f"Found solicitud: {solicitud.codigo}")
            
            # Find all analyst comment records for this solicitud
            analyst_comments = CalificacionCampo.objects.filter(
                solicitud=solicitud,
                campo__startswith='comentario_analista_credito'
            ).order_by('fecha_creacion')
            
            print(f"\nFound {analyst_comments.count()} analyst comment records:")
            for comment in analyst_comments:
                comment_preview = comment.comentario[:50] if comment.comentario else "No comment"
                print(f"  - {comment.campo}: {comment_preview}... ({comment.fecha_creacion})")
            
            if analyst_comments.count() > 1:
                # Keep the most recent one and get its data
                latest_comment = analyst_comments.last()
                if latest_comment:
                    print(f"\nKeeping latest comment: {latest_comment.campo}")
                    print(f"Comment: {latest_comment.comentario or 'No comment'}")
                    print(f"Result: {latest_comment.resultado_analisis or 'No result'}")
                    
                    # Create a new record with the standard field name if it doesn't exist
                    standard_field_name = "comentario_analista_credito"
                    
                    with transaction.atomic():
                        # Update or create the standard record
                        standard_comment, created = CalificacionCampo.objects.update_or_create(
                            solicitud=solicitud,
                            campo=standard_field_name,
                            defaults={
                                'estado': latest_comment.estado or 'sin_calificar',
                                'comentario': latest_comment.comentario or '',
                                'resultado_analisis': latest_comment.resultado_analisis or '',
                                'usuario': latest_comment.usuario,
                                'fecha_modificacion': timezone.now()
                            }
                        )
                        
                        if created:
                            print(f"\nCreated new standard record: {standard_field_name}")
                        else:
                            print(f"\nUpdated existing standard record: {standard_field_name}")
                        
                        # Delete all the timestamped records
                        timestamped_records = analyst_comments.exclude(campo=standard_field_name)
                        deleted_count = timestamped_records.count()
                        timestamped_records.delete()
                        
                        print(f"Deleted {deleted_count} duplicate timestamped records")
            
            # Verify final state
            final_comments = CalificacionCampo.objects.filter(
                solicitud=solicitud,
                campo__startswith='comentario_analista_credito'
            )
            
            print(f"\nFinal state: {final_comments.count()} analyst comment record(s)")
            for comment in final_comments:
                print(f"  - {comment.campo}: {comment.resultado_analisis or 'No result'}")
            
            print("\n✅ Cleanup completed successfully!")
            print("\nThe API has been fixed to use update_or_create instead of create.")
            print("Now when you submit analyst comments, they will update the existing record.")
            
        except Solicitud.DoesNotExist:
            print(f"Solicitud {solicitud_codigo} not found")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"Setup error: {e}")
    import traceback
    traceback.print_exc()
