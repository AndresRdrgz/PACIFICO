# Generated manually to replace problematic ClienteEntrevista table fix
# This migration safely handles the table creation/recreation for production

from django.db import migrations, models, connection
import django.contrib.auth.models
import django.db.models.deletion


def create_clienteentrevista_table_safe(apps, schema_editor):
    """Safely create ClienteEntrevista table with error handling"""
    
    # Check if table already exists with correct structure
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'workflow_clienteentrevista' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Expected key columns that should exist
            required_columns = ['primer_nombre', 'primer_apellido', 'sexo', 'salario']
            
            if all(col in existing_columns for col in required_columns):
                print("✅ Table workflow_clienteentrevista already exists with correct structure")
                return
                
        except Exception as e:
            print(f"⚠️  Could not check existing table: {e}")
    
    # Create the table
    create_sql = """
    CREATE TABLE IF NOT EXISTS workflow_clienteentrevista (
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
        fecha_completada_admin TIMESTAMP WITH TIME ZONE,
        CHECK (no_dependientes >= 0)
    );
    """
    
    # Constraints to add (only if table creation succeeds)
    constraints = [
        ("workflow_clienteentrevista_sexo_check", "sexo IN ('M', 'F')"),
        ("workflow_clienteentrevista_provincia_cedula_check", "provincia_cedula IN ('', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')"),
        ("workflow_clienteentrevista_tipo_letra_check", "tipo_letra IN ('', 'E', 'N', 'PE', 'AV')"),
        ("workflow_clienteentrevista_tipo_producto_check", "tipo_producto IN ('Auto', 'Personal', 'Hipotecario')"),
        ("workflow_clienteentrevista_estado_civil_check", "estado_civil IN ('CASADO (A)', 'UNIDO (A)', 'SOLTERO (A)', 'VIUDO (A)', 'SEPARADO (A)')"),
        ("workflow_clienteentrevista_tipo_trabajo_check", "tipo_trabajo IN ('ASALARIADO', 'INDEPENDIENTE', 'ABOGADO')"),
        ("workflow_clienteentrevista_frecuencia_pago_check", "frecuencia_pago IN ('SEMANAL', 'QUINCENAL', 'MENSUAL')"),
        ("workflow_clienteentrevista_origen_fondos_check", "origen_fondos IN ('LOCAL', 'EXTRANJERO')"),
    ]
    
    with connection.cursor() as cursor:
        try:
            # Create the table
            cursor.execute(create_sql)
            print("✅ Created workflow_clienteentrevista table")
            
            # Add constraints only if table exists and has the columns
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'workflow_clienteentrevista' AND column_name = 'sexo'")
            if cursor.fetchone():
                for constraint_name, constraint_condition in constraints:
                    try:
                        # Check if constraint already exists
                        cursor.execute("""
                            SELECT constraint_name 
                            FROM information_schema.constraint_column_usage 
                            WHERE table_name = 'workflow_clienteentrevista' 
                            AND constraint_name = %s
                        """, [constraint_name])
                        
                        if not cursor.fetchone():
                            cursor.execute(f"ALTER TABLE workflow_clienteentrevista ADD CONSTRAINT {constraint_name} CHECK ({constraint_condition})")
                            print(f"✅ Added constraint: {constraint_name}")
                        else:
                            print(f"ℹ️  Constraint {constraint_name} already exists")
                    except Exception as e:
                        print(f"⚠️  Warning adding constraint {constraint_name}: {e}")
            else:
                print("⚠️  Column 'sexo' not found, skipping constraints")
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            raise


def reverse_create_clienteentrevista_table_safe(apps, schema_editor):
    """Reverse the table creation"""
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista CASCADE")
        print("🗑️  Dropped workflow_clienteentrevista table")


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        # Use RunPython instead of RunSQL for better error handling
        migrations.RunPython(
            create_clienteentrevista_table_safe,
            reverse_create_clienteentrevista_table_safe,
            # State operations - tell Django what we're doing
            state_operations=[
                migrations.CreateModel(
                    name='ClienteEntrevista',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('primer_nombre', models.CharField(max_length=100)),
                        ('segundo_nombre', models.CharField(blank=True, max_length=100, null=True)),
                        ('primer_apellido', models.CharField(max_length=100)),
                        ('segundo_apellido', models.CharField(blank=True, max_length=100, null=True)),
                        ('provincia_cedula', models.CharField(blank=True, choices=[('', '—'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], max_length=2, null=True)),
                        ('tipo_letra', models.CharField(blank=True, choices=[('', '—'), ('E', 'E'), ('N', 'N'), ('PE', 'PE'), ('AV', 'AV')], max_length=5, null=True)),
                        ('tomo_cedula', models.CharField(max_length=10)),
                        ('partida_cedula', models.CharField(max_length=10)),
                        ('telefono', models.CharField(max_length=20)),
                        ('email', models.EmailField(max_length=254)),
                        ('fecha_nacimiento', models.DateField()),
                        ('sexo', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1)),
                        ('jubilado', models.BooleanField(default=False)),
                        ('nivel_academico', models.CharField(blank=True, help_text='Valores separados por coma para selección múltiple. Ej: PRIMARIA,SECUNDARIA', max_length=200, null=True)),
                        ('lugar_nacimiento', models.CharField(blank=True, max_length=100, null=True)),
                        ('estado_civil', models.CharField(blank=True, choices=[('CASADO (A)', 'CASADO (A)'), ('UNIDO (A)', 'UNIDO (A)'), ('SOLTERO (A)', 'SOLTERO (A)'), ('VIUDO (A)', 'VIUDO (A)'), ('SEPARADO (A)', 'SEPARADO (A)')], max_length=20, null=True)),
                        ('no_dependientes', models.PositiveIntegerField(default=0)),
                        ('titulo', models.CharField(blank=True, max_length=100, null=True)),
                        ('salario', models.DecimalField(decimal_places=2, max_digits=10)),
                        ('tipo_producto', models.CharField(choices=[('Auto', 'Auto'), ('Personal', 'Personal'), ('Hipotecario', 'Hipotecario')], max_length=50)),
                        ('oficial', models.CharField(max_length=100)),
                        ('apellido_casada', models.CharField(blank=True, max_length=100, null=True)),
                        ('peso', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Peso (lb)')),
                        ('estatura', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Estatura (m)')),
                        ('nacionalidad', models.CharField(default='Panamá', max_length=100)),
                        ('direccion_completa', models.TextField(blank=True, null=True)),
                        ('barrio', models.CharField(blank=True, max_length=100, null=True)),
                        ('calle', models.CharField(blank=True, max_length=100, null=True)),
                        ('casa_apto', models.CharField(blank=True, max_length=100, null=True)),
                        ('conyuge_nombre', models.CharField(blank=True, max_length=100, null=True)),
                        ('conyuge_cedula', models.CharField(blank=True, max_length=15, null=True)),
                        ('conyuge_lugar_trabajo', models.CharField(blank=True, max_length=100, null=True)),
                        ('conyuge_cargo', models.CharField(blank=True, max_length=100, null=True)),
                        ('conyuge_ingreso', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                        ('conyuge_telefono', models.CharField(blank=True, max_length=20, null=True)),
                        ('trabajo_direccion', models.TextField(blank=True, null=True)),
                        ('trabajo_lugar', models.CharField(blank=True, max_length=100, null=True)),
                        ('trabajo_cargo', models.CharField(blank=True, max_length=100, null=True)),
                        ('tipo_trabajo', models.CharField(blank=True, choices=[('ASALARIADO', 'ASALARIADO'), ('INDEPENDIENTE', 'INDEPENDIENTE'), ('ABOGADO', 'ABOGADO')], max_length=20, null=True)),
                        ('frecuencia_pago', models.CharField(blank=True, choices=[('SEMANAL', 'SEMANAL'), ('QUINCENAL', 'QUINCENAL'), ('MENSUAL', 'MENSUAL')], max_length=20, null=True)),
                        ('tel_trabajo', models.CharField(blank=True, max_length=10, null=True)),
                        ('tel_ext', models.CharField(blank=True, max_length=5, null=True)),
                        ('origen_fondos', models.CharField(blank=True, choices=[('LOCAL', 'LOCAL'), ('EXTRANJERO', 'EXTRANJERO')], max_length=20, null=True)),
                        ('fecha_inicio_trabajo', models.DateField(blank=True, null=True)),
                        ('tipo_ingreso_1', models.CharField(blank=True, max_length=100, null=True)),
                        ('descripcion_ingreso_1', models.CharField(blank=True, max_length=255, null=True)),
                        ('monto_ingreso_1', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                        ('tipo_ingreso_2', models.CharField(blank=True, max_length=100, null=True)),
                        ('descripcion_ingreso_2', models.CharField(blank=True, max_length=255, null=True)),
                        ('monto_ingreso_2', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                        ('tipo_ingreso_3', models.CharField(blank=True, max_length=100, null=True)),
                        ('descripcion_ingreso_3', models.CharField(blank=True, max_length=255, null=True)),
                        ('monto_ingreso_3', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                        ('es_pep', models.BooleanField(default=False)),
                        ('pep_ingreso', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                        ('pep_inicio', models.DateField(blank=True, null=True)),
                        ('pep_cargo_actual', models.CharField(blank=True, max_length=100, null=True)),
                        ('pep_fin', models.DateField(blank=True, null=True)),
                        ('pep_cargo_anterior', models.CharField(blank=True, max_length=100, null=True)),
                        ('pep_fin_anterior', models.DateField(blank=True, null=True)),
                        ('es_familiar_pep', models.BooleanField(default=False)),
                        ('parentesco_pep', models.CharField(blank=True, max_length=50, null=True)),
                        ('nombre_pep', models.CharField(blank=True, max_length=100, null=True)),
                        ('cargo_pep', models.CharField(blank=True, max_length=100, null=True)),
                        ('institucion_pep', models.CharField(blank=True, max_length=100, null=True)),
                        ('pep_fam_inicio', models.DateField(blank=True, null=True)),
                        ('pep_fam_fin', models.DateField(blank=True, null=True)),
                        ('banco', models.CharField(blank=True, max_length=100, null=True)),
                        ('tipo_cuenta', models.CharField(blank=True, max_length=50, null=True)),
                        ('numero_cuenta', models.CharField(blank=True, max_length=20, null=True)),
                        ('autoriza_apc', models.BooleanField(default=False)),
                        ('acepta_datos', models.BooleanField(default=False)),
                        ('es_beneficiario_final', models.BooleanField(default=False)),
                        ('fecha_entrevista', models.DateTimeField(auto_now_add=True)),
                        ('empresa', models.CharField(blank=True, max_length=100, null=True)),
                        ('completada_por_admin', models.BooleanField(default=False)),
                        ('fecha_completada_admin', models.DateTimeField(blank=True, null=True)),
                    ],
                ),
            ]
        ),
    ]
