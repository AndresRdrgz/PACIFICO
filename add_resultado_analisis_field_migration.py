#!/usr/bin/env python3
"""
Migration script to add resultado_analisis field to CalificacionCampo model
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/andresrdrgz_/Documents/GitHub/PACIFICO')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from django.db import connection

def run_migration():
    """Execute the SQL to add resultado_analisis field"""
    
    with connection.cursor() as cursor:
        try:
            # Add the resultado_analisis field to CalificacionCampo model
            cursor.execute("""
                ALTER TABLE workflow_calificacioncampo 
                ADD COLUMN resultado_analisis VARCHAR(20) NULL;
            """)
            
            print("✅ Campo resultado_analisis agregado exitosamente a CalificacionCampo")
            
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("⚠️  El campo resultado_analisis ya existe en CalificacionCampo")
            else:
                print(f"❌ Error al agregar campo resultado_analisis: {e}")
                raise

if __name__ == "__main__":
    print("🔧 Ejecutando migración para agregar campo resultado_analisis...")
    run_migration()
    print("✅ Migración completada")
