# Generated manually - Simple emergency migration for ClienteEntrevista
# This migration creates the table if it doesn't exist

from django.db import migrations, models
import django.db.models.deletion


def create_table_if_not_exists(apps, schema_editor):
    """Create ClienteEntrevista table if it doesn't exist"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'workflow_clienteentrevista'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Create table using Django's schema editor
            ClienteEntrevista = apps.get_model('workflow', 'ClienteEntrevista')
            schema_editor.create_model(ClienteEntrevista)
            print("Created workflow_clienteentrevista table")
        else:
            print("Table workflow_clienteentrevista already exists")


def reverse_create_table(apps, schema_editor):
    """Reverse the table creation"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS workflow_clienteentrevista CASCADE")


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0055_add_solicitud_completa_event_type'),
    ]

    operations = [
        migrations.RunPython(
            create_table_if_not_exists,
            reverse_create_table,
        ),
    ]
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
