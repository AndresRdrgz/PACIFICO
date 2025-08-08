#!/usr/bin/env python3
"""
Production Database Repair Script for ClienteEntrevista table
This script helps diagnose and fix table issues in production PostgreSQL database.
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection, transaction
from django.core.management import execute_from_command_line

# Add the project directory to the Python path
sys.path.append('/www/wwwroot/PACIFICO')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def check_table_structure(table_name):
    """Check table structure and return column information"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, [table_name])
            return cursor.fetchall()
        except Exception as e:
            print(f"Error checking table structure: {e}")
            return []

def create_clienteentrevista_table():
    """Create the ClienteEntrevista table with correct structure"""
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
        nacionalidad VARCHAR(100) NOT NULL DEFAULT 'Panamá',
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
    
    constraints_sql = [
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_sexo_check CHECK (sexo IN ('M', 'F'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_provincia_cedula_check CHECK (provincia_cedula IN ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_tipo_letra_check CHECK (tipo_letra IN ('', 'E', 'N', 'PE', 'AV'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_tipo_producto_check CHECK (tipo_producto IN ('Auto', 'Personal', 'Hipotecario'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_estado_civil_check CHECK (estado_civil IN ('CASADO (A)', 'UNIDO (A)', 'SOLTERO (A)', 'VIUDO (A)', 'SEPARADO (A)'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_tipo_trabajo_check CHECK (tipo_trabajo IN ('ASALARIADO', 'INDEPENDIENTE', 'ABOGADO'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_frecuencia_pago_check CHECK (frecuencia_pago IN ('SEMANAL', 'QUINCENAL', 'MENSUAL'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_origen_fondos_check CHECK (origen_fondos IN ('LOCAL', 'EXTRANJERO'));",
        "ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT workflow_clienteentrevista_no_dependientes_check CHECK (no_dependientes >= 0);"
    ]
    
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Create the main table
            cursor.execute(create_sql)
            print("✅ Created workflow_clienteentrevista table")
            
            # Add constraints
            for constraint in constraints_sql:
                try:
                    cursor.execute(constraint)
                    print(f"✅ Added constraint: {constraint[:50]}...")
                except Exception as e:
                    print(f"⚠️  Warning adding constraint: {e}")

def main():
    """Main diagnostic and repair function"""
    print("🔍 PostgreSQL Database Diagnostic Script")
    print("=" * 50)
    
    table_name = 'workflow_clienteentrevista'
    
    # Check if table exists
    try:
        table_exists = check_table_exists(table_name)
        print(f"Table {table_name} exists: {table_exists}")
    except Exception as e:
        print(f"❌ Error checking table existence: {e}")
        return
    
    if table_exists:
        # Check table structure
        print(f"\n🔍 Checking structure of {table_name}:")
        columns = check_table_structure(table_name)
        if columns:
            print(f"Found {len(columns)} columns:")
            for col in columns[:5]:  # Show first 5 columns
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            if len(columns) > 5:
                print(f"  ... and {len(columns) - 5} more columns")
            
            # Test basic query
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"✅ Table has {count} records")
            except Exception as e:
                print(f"❌ Error querying table: {e}")
                print("🔧 Table structure might be incomplete. Consider recreating.")
                
                # Ask if user wants to recreate
                response = input("\nRecreate table? (y/N): ")
                if response.lower() == 'y':
                    print("🔧 Dropping and recreating table...")
                    with transaction.atomic():
                        with connection.cursor() as cursor:
                            cursor.execute(f"DROP TABLE {table_name} CASCADE")
                            print(f"✅ Dropped table {table_name}")
                    create_clienteentrevista_table()
        else:
            print("❌ Could not retrieve table structure")
    else:
        print(f"\n🔧 Table {table_name} does not exist. Creating...")
        create_clienteentrevista_table()
    
    # Final verification
    print(f"\n🔍 Final verification:")
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT primer_nombre FROM {table_name} LIMIT 1")
            print("✅ Table structure is correct")
    except Exception as e:
        print(f"❌ Table still has issues: {e}")
    
    print(f"\n✅ Diagnostic complete. You can now try running migrations.")

if __name__ == "__main__":
    main()
