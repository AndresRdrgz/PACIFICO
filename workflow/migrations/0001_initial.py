# Generated by Django 5.1.3 on 2025-06-24 15:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
                ('no_dependientes', models.PositiveIntegerField(default=0)),
                ('titulo', models.CharField(blank=True, max_length=100, null=True)),
                ('tipo_producto', models.CharField(choices=[('Auto', 'Auto'), ('Personal', 'Personal'), ('Hipotecario', 'Hipotecario')], max_length=50)),
                ('oficial', models.CharField(max_length=100)),
                ('apellido_casada', models.CharField(blank=True, max_length=100, null=True)),
                ('peso', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Peso (lb)')),
                ('estatura', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Estatura (m)')),
                ('nacionalidad', models.CharField(default='Panamá', max_length=100)),
                ('estado_civil', models.CharField(blank=True, choices=[('CASADO (A)', 'CASADO (A)'), ('UNIDO (A)', 'UNIDO (A)'), ('SOLTERO (A)', 'SOLTERO (A)'), ('VIUDO (A)', 'VIUDO (A)'), ('SEPARADO (A)', 'SEPARADO (A)')], max_length=20, null=True)),
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
                ('salario', models.DecimalField(decimal_places=2, max_digits=10)),
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
            ],
        ),
        migrations.CreateModel(
            name='OtroIngreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_ingreso', models.CharField(blank=True, choices=[('', '---------'), ('LOCAL', 'LOCAL'), ('EXTRANJERO', 'EXTRANJERO')], default='', max_length=20, null=True)),
                ('fuente', models.CharField(max_length=100)),
                ('monto', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otros_ingresos', to='workflow.clienteentrevista')),
            ],
        ),
        migrations.CreateModel(
            name='ReferenciaComercial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(blank=True, choices=[('', '---------'), ('COMERCIAL', 'COMERCIAL'), ('CLIENTES', 'CLIENTES')], max_length=100, null=True)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('actividad', models.CharField(blank=True, max_length=100, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('celular', models.CharField(blank=True, max_length=20, null=True)),
                ('saldo', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('entrevista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referencias_comerciales', to='workflow.clienteentrevista')),
            ],
        ),
        migrations.CreateModel(
            name='ReferenciaPersonal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=20)),
                ('relacion', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('entrevista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referencias_personales', to='workflow.clienteentrevista')),
            ],
        ),
    ]
