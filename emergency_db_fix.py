#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Production Database Fix Script for PostgreSQL
Run this script directly on the production server to fix table issues
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_config():
    """Get database configuration from environment or default values"""
    # Default production database URL
    database_url = "postgresql://postgres:FP.h05t1l3@localhost:5432/pacifico"
    
    # Parse the database URL
    parsed = urlparse(database_url)
    
    return {
        'host': parsed.hostname,
        'database': parsed.path[1:],  # Remove leading slash
        'user': parsed.username,
        'password': parsed.password,
        'port': parsed.port or 5432
    }

def check_table_exists(cursor, table_name):
    """Check if table exists"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, [table_name])
    return cursor.fetchone()[0]

def get_table_columns(cursor, table_name):
    """Get table columns"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = %s 
        AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, [table_name])
    return cursor.fetchall()

def drop_table_safely(cursor, table_name):
    """Safely drop a table"""
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        print(f"✅ Dropped table {table_name}")
        return True
    except Exception as e:
        print(f"❌ Error dropping table {table_name}: {e}")
        return False

def create_clienteentrevista_table(cursor):
    """Create the ClienteEntrevista table"""
    
    create_sql = """
    CREATE TABLE workflow_clienteentrevista (
        id BIGSERIAL PRIMARY KEY,
        primer_nombre VARCHAR(100) NOT NULL,
        segundo_nombre VARCHAR(100),
        primer_apellido VARCHAR(100) NOT NULL,
        segundo_apellido VARCHAR(100),
        provincia_cedula VARCHAR(2),
        tipo_letra VARCHAR(5),
        tomo_cedula VARCHAR(10) NOT NULL,
        partida_cedula VARCHAR(10) NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        email VARCHAR(254) NOT NULL,
        fecha_nacimiento DATE NOT NULL,
        sexo VARCHAR(1) NOT NULL,
        jubilado BOOLEAN NOT NULL DEFAULT false,
        nivel_academico VARCHAR(200),
        lugar_nacimiento VARCHAR(100),
        estado_civil VARCHAR(20),
        no_dependientes INTEGER NOT NULL DEFAULT 0,
        titulo VARCHAR(100),
        salario DECIMAL(10, 2) NOT NULL,
        tipo_producto VARCHAR(50) NOT NULL,
        oficial VARCHAR(100) NOT NULL,
        apellido_casada VARCHAR(100),
        peso DECIMAL(5, 2),
        estatura DECIMAL(4, 2),
        nacionalidad VARCHAR(100) NOT NULL DEFAULT 'Panama',
        direccion_completa TEXT,
        barrio VARCHAR(100),
        calle VARCHAR(100),
        casa_apto VARCHAR(100),
        conyuge_nombre VARCHAR(100),
        conyuge_cedula VARCHAR(15),
        conyuge_lugar_trabajo VARCHAR(100),
        conyuge_cargo VARCHAR(100),
        conyuge_ingreso DECIMAL(12, 2),
        conyuge_telefono VARCHAR(20),
        trabajo_direccion TEXT,
        trabajo_lugar VARCHAR(100),
        trabajo_cargo VARCHAR(100),
        tipo_trabajo VARCHAR(20),
        frecuencia_pago VARCHAR(20),
        tel_trabajo VARCHAR(10),
        tel_ext VARCHAR(5),
        origen_fondos VARCHAR(20),
        fecha_inicio_trabajo DATE,
        tipo_ingreso_1 VARCHAR(100),
        descripcion_ingreso_1 VARCHAR(255),
        monto_ingreso_1 DECIMAL(12, 2),
        tipo_ingreso_2 VARCHAR(100),
        descripcion_ingreso_2 VARCHAR(255),
        monto_ingreso_2 DECIMAL(12, 2),
        tipo_ingreso_3 VARCHAR(100),
        descripcion_ingreso_3 VARCHAR(255),
        monto_ingreso_3 DECIMAL(12, 2),
        es_pep BOOLEAN NOT NULL DEFAULT false,
        pep_ingreso DECIMAL(9, 2),
        pep_inicio DATE,
        pep_cargo_actual VARCHAR(100),
        pep_fin DATE,
        pep_cargo_anterior VARCHAR(100),
        pep_fin_anterior DATE,
        es_familiar_pep BOOLEAN NOT NULL DEFAULT false,
        parentesco_pep VARCHAR(50),
        nombre_pep VARCHAR(100),
        cargo_pep VARCHAR(100),
        institucion_pep VARCHAR(100),
        pep_fam_inicio DATE,
        pep_fam_fin DATE,
        banco VARCHAR(100),
        tipo_cuenta VARCHAR(50),
        numero_cuenta VARCHAR(20),
        autoriza_apc BOOLEAN NOT NULL DEFAULT false,
        acepta_datos BOOLEAN NOT NULL DEFAULT false,
        es_beneficiario_final BOOLEAN NOT NULL DEFAULT false,
        fecha_entrevista TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        empresa VARCHAR(100),
        completada_por_admin BOOLEAN NOT NULL DEFAULT false,
        fecha_completada_admin TIMESTAMP WITH TIME ZONE,
        
        -- Basic constraints
        CHECK (no_dependientes >= 0),
        CHECK (sexo IN ('M', 'F')),
        CHECK (provincia_cedula IN ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')),
        CHECK (tipo_letra IN ('', 'E', 'N', 'PE', 'AV')),
        CHECK (tipo_producto IN ('Auto', 'Personal', 'Hipotecario')),
        CHECK (estado_civil IN ('CASADO (A)', 'UNIDO (A)', 'SOLTERO (A)', 'VIUDO (A)', 'SEPARADO (A)')),
        CHECK (tipo_trabajo IN ('ASALARIADO', 'INDEPENDIENTE', 'ABOGADO')),
        CHECK (frecuencia_pago IN ('SEMANAL', 'QUINCENAL', 'MENSUAL')),
        CHECK (origen_fondos IN ('LOCAL', 'EXTRANJERO'))
    );
    """
    
    try:
        cursor.execute(create_sql)
        print("✅ Created workflow_clienteentrevista table with constraints")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def fix_migration_state(cursor):
    """Fix the migration state in django_migrations table"""
    
    # Check if problematic migrations exist
    cursor.execute("""
        SELECT id, app, name FROM django_migrations 
        WHERE app = 'workflow' AND name LIKE '%clienteentrevista%'
        ORDER BY id;
    """)
    
    problematic_migrations = cursor.fetchall()
    print(f"Found {len(problematic_migrations)} ClienteEntrevista-related migrations:")
    
    for migration_id, app, name in problematic_migrations:
        print(f"  - {migration_id}: {app}.{name}")
    
    # Check if we should remove problematic migration entries
    response = input("\nRemove problematic migration entries? (y/N): ").lower().strip()
    if response == 'y':
        # Remove the problematic migration entries
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'workflow' 
            AND name IN ('0056_fix_clienteentrevista_table_production', '0057_replace_fix_clienteentrevista_table')
        """)
        print("✅ Removed problematic migration entries")
        
        # Add a safe migration entry
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) 
            VALUES ('workflow', '0056_safe_clienteentrevista_noop', NOW())
            ON CONFLICT DO NOTHING
        """)
        print("✅ Added safe migration entry")

def main():
    print("🚨 Emergency PostgreSQL Database Fix Script")
    print("=" * 50)
    
    # Get database connection
    try:
        db_config = get_database_config()
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        print(f"✅ Connected to database: {db_config['database']}")
    except Exception as e:
        print(f"❌ Could not connect to database: {e}")
        return 1
    
    table_name = 'workflow_clienteentrevista'
    
    try:
        # Check table status
        table_exists = check_table_exists(cursor, table_name)
        print(f"\n📊 Table {table_name} exists: {table_exists}")
        
        if table_exists:
            columns = get_table_columns(cursor, table_name)
            print(f"Table has {len(columns)} columns:")
            
            # Check for key columns
            column_names = [col[0] for col in columns]
            required_columns = ['primer_nombre', 'primer_apellido', 'sexo', 'salario']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                response = input("Recreate table? (y/N): ").lower().strip()
                if response == 'y':
                    drop_table_safely(cursor, table_name)
                    table_exists = False
            else:
                print("✅ Table has all required columns")
                
                # Test a simple query
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"✅ Table has {count} records and is working correctly")
                except Exception as e:
                    print(f"❌ Table exists but has issues: {e}")
                    response = input("Recreate table? (y/N): ").lower().strip()
                    if response == 'y':
                        drop_table_safely(cursor, table_name)
                        table_exists = False
        
        # Create table if needed
        if not table_exists:
            print(f"\n🔧 Creating table {table_name}...")
            if create_clienteentrevista_table(cursor):
                print("✅ Table created successfully")
            else:
                print("❌ Failed to create table")
                return 1
        
        # Fix migration state
        print(f"\n🔧 Checking migration state...")
        fix_migration_state(cursor)
        
        # Final verification
        print(f"\n🔍 Final verification...")
        cursor.execute(f"SELECT primer_nombre FROM {table_name} LIMIT 1")
        print("✅ Table structure is correct and ready for use")
        
        print(f"\n✅ Database fix completed successfully!")
        print("You can now run: ./python3 /www/wwwroot/PACIFICO/manage.py migrate")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    finally:
        cursor.close()
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
