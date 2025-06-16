from django.contrib import admin
from .models import ClienteEntrevista, ReferenciaPersonal, ReferenciaComercial, OtroIngreso

@admin.register(ClienteEntrevista)
class ClienteEntrevistaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
        'provincia_cedula', 'tipo_letra', 'tomo_cedula', 'partida_cedula',
        'telefono', 'email', 'fecha_nacimiento', 'sexo', 'jubilado', 'nivel_academico',
        'estado_civil', 'no_dependientes', 'titulo', 'salario', 'tipo_producto', 'oficial',
        'apellido_casada', 'peso', 'estatura', 'nacionalidad', 'direccion_completa',
        'barrio', 'calle', 'casa_apto', 'conyuge_nombre', 'conyuge_cedula',
        'conyuge_lugar_trabajo', 'conyuge_cargo', 'conyuge_ingreso', 'conyuge_telefono',
        'trabajo_direccion', 'trabajo_lugar', 'trabajo_cargo', 'tipo_trabajo',
        'frecuencia_pago', 'tel_trabajo', 'tel_ext', 'origen_fondos', 'fecha_inicio_trabajo',
        'tipo_ingreso_1', 'descripcion_ingreso_1', 'monto_ingreso_1',
        'tipo_ingreso_2', 'descripcion_ingreso_2', 'monto_ingreso_2',
        'tipo_ingreso_3', 'descripcion_ingreso_3', 'monto_ingreso_3',
        'es_pep', 'pep_ingreso', 'pep_inicio', 'pep_cargo_actual', 'pep_fin',
        'pep_cargo_anterior', 'pep_fin_anterior', 'es_familiar_pep', 'parentesco_pep',
        'nombre_pep', 'cargo_pep', 'institucion_pep', 'pep_fam_inicio', 'pep_fam_fin',
        'banco', 'tipo_cuenta', 'numero_cuenta', 'autoriza_apc', 'acepta_datos',
        'es_beneficiario_final', 'fecha_entrevista'
    )
    list_display_links = ('id', 'primer_nombre', 'primer_apellido')
    search_fields = (
        'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
        'email', 'telefono', 'tomo_cedula', 'partida_cedula'
    )
    list_filter = ('tipo_producto', 'oficial', 'fecha_entrevista', 'sexo', 'estado_civil', 'jubilado')
    list_per_page = 25


@admin.register(ReferenciaPersonal)
class ReferenciaPersonalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'relacion', 'direccion', 'entrevista')
    list_display_links = ('nombre',)
    search_fields = ('nombre', 'telefono', 'relacion')
    list_per_page = 25


@admin.register(ReferenciaComercial)
class ReferenciaComercialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'actividad', 'telefono', 'entrevista')
    list_display_links = ('nombre',)
    search_fields = ('nombre', 'tipo', 'actividad', 'telefono')
    list_per_page = 25


@admin.register(OtroIngreso)
class OtroIngresoAdmin(admin.ModelAdmin):
    list_display = ('tipo_ingreso', 'fuente', 'monto', 'cliente')
    list_display_links = ('fuente',)
    search_fields = ('fuente',)
    list_per_page = 25
