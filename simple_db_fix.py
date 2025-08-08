#!/usr/bin/env python3
"""
Simple Emergency Database Fix Script - No Special Characters
Run this script directly on the production server
"""

import os
import sys
import psycopg2

def main():
    print("Emergency PostgreSQL Database Fix Script")
    print("=" * 50)
    
    # Database connection
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='pacifico',
            user='postgres',
            password='FP.h05t1l3',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to database successfully")
    except Exception as e:
        print(f"Could not connect to database: {e}")
        return 1
    
    table_name = 'workflow_clienteentrevista'
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        
        table_exists = cursor.fetchone()[0]
        print(f"Table {table_name} exists: {table_exists}")
        
        if table_exists:
            # Check table structure
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, [table_name])
            
            columns = [row[0] for row in cursor.fetchall()]
            required_columns = ['primer_nombre', 'primer_apellido', 'sexo', 'salario']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"Missing required columns: {missing_columns}")
                response = input("Recreate table? (y/N): ").lower().strip()
                if response == 'y':
                    cursor.execute(f"DROP TABLE {table_name} CASCADE")
                    print(f"Dropped table {table_name}")
                    table_exists = False
            else:
                print("Table has all required columns")
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"Table has {count} records and is working correctly")
                    return 0
                except Exception as e:
                    print(f"Table exists but has issues: {e}")
                    response = input("Recreate table? (y/N): ").lower().strip()
                    if response == 'y':
                        cursor.execute(f"DROP TABLE {table_name} CASCADE")
                        print(f"Dropped table {table_name}")
                        table_exists = False
        
        if not table_exists:
            print(f"Creating table {table_name}...")
            
            # Simple table creation without special characters
            create_sql = f"""
            CREATE TABLE {table_name} (
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
                fecha_completada_admin TIMESTAMP WITH TIME ZONE
            );
            """
            
            cursor.execute(create_sql)
            print("Table created successfully")
            
            # Add basic constraints
            constraints = [
                "CHECK (no_dependientes >= 0)",
                "CHECK (sexo IN ('M', 'F'))",
            ]
            
            for i, constraint in enumerate(constraints):
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {table_name}_check_{i} {constraint}")
                    print(f"Added constraint {i}")
                except Exception as e:
                    print(f"Warning adding constraint {i}: {e}")
        
        # Fix migration state
        print("Checking migration state...")
        cursor.execute("""
            DELETE FROM django_migrations 
            WHERE app = 'workflow' 
            AND name IN ('0056_fix_clienteentrevista_table_production', '0057_replace_fix_clienteentrevista_table')
        """)
        
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) 
            VALUES ('workflow', '0056_safe_clienteentrevista_noop', NOW())
            ON CONFLICT DO NOTHING
        """)
        print("Fixed migration state")
        
        # Final verification
        cursor.execute(f"SELECT primer_nombre FROM {table_name} LIMIT 1")
        print("Database fix completed successfully!")
        print("You can now run: ./python3 /www/wwwroot/PACIFICO/manage.py migrate")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    finally:
        cursor.close()
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
