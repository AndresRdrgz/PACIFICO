from django.contrib import admin
from .models import ClienteEntrevista, ReferenciaPersonal, ReferenciaComercial, OtroIngreso
from .modelsWorkflow import Pipeline, Etapa, SubEstado, TransicionEtapa, PermisoEtapa, Solicitud, HistorialSolicitud, Requisito, RequisitoPipeline, RequisitoSolicitud, CampoPersonalizado, ValorCampoSolicitud, RequisitoTransicion, PermisoPipeline, PermisoBandeja, CalificacionCampo, SolicitudComentario, NivelComite, UsuarioNivelComite, ParticipacionComite, SolicitudEscalamientoComite
from .forms import SolicitudAdminForm

class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 1

class SubEstadoInline(admin.TabularInline):
    model = SubEstado
    extra = 1
    fk_name = 'pipeline'  # Specify which ForeignKey to use since SubEstado has two FKs

class TransicionEtapaInline(admin.TabularInline):
    model = TransicionEtapa
    extra = 1

class RequisitoPipelineInline(admin.TabularInline):
    model = RequisitoPipeline
    extra = 1

class CampoPersonalizadoInline(admin.TabularInline):
    model = CampoPersonalizado
    extra = 1

class PermisoPipelineInline(admin.TabularInline):
    model = PermisoPipeline
    extra = 1

class PermisoBandejaInline(admin.TabularInline):
    model = PermisoBandeja
    extra = 1

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


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    inlines = [EtapaInline, SubEstadoInline, TransicionEtapaInline, RequisitoPipelineInline, CampoPersonalizadoInline]


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'nombre', 'orden', 'sla', 'es_bandeja_grupal')
    search_fields = ('nombre', 'pipeline__nombre')
    list_filter = ('pipeline',)


@admin.register(SubEstado)
class SubEstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'etapa', 'nombre', 'orden')
    search_fields = ('nombre', 'etapa__nombre')
    list_filter = ('etapa',)


@admin.register(TransicionEtapa)
class TransicionEtapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'etapa_origen', 'etapa_destino', 'nombre', 'requiere_permiso')
    search_fields = ('nombre', 'pipeline__nombre', 'etapa_origen__nombre', 'etapa_destino__nombre')
    list_filter = ('pipeline',)


@admin.register(PermisoEtapa)
class PermisoEtapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'etapa', 'grupo', 'puede_ver', 'puede_autoasignar')
    search_fields = ('etapa__nombre', 'grupo__name')
    list_filter = ('etapa', 'grupo')


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    form = SolicitudAdminForm
    list_display = ('id', 'codigo', 'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a', 'fecha_creacion', 'fecha_ultima_actualizacion')
    search_fields = ('codigo', 'pipeline__nombre')
    list_filter = ('pipeline', 'etapa_actual', 'subestado_actual')


@admin.register(HistorialSolicitud)
class HistorialSolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'etapa', 'subestado', 'usuario_responsable', 'fecha_inicio', 'fecha_fin')
    search_fields = ('solicitud__codigo', 'etapa__nombre', 'subestado__nombre')
    list_filter = ('etapa', 'subestado')


@admin.register(Requisito)
class RequisitoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(RequisitoPipeline)
class RequisitoPipelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'requisito', 'obligatorio')
    search_fields = ('pipeline__nombre', 'requisito__nombre')
    list_filter = ('pipeline',)


@admin.register(RequisitoSolicitud)
class RequisitoSolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'requisito', 'archivo', 'cumplido', 'observaciones')
    search_fields = ('solicitud__codigo', 'requisito__nombre')
    list_filter = ('solicitud', 'requisito')


@admin.register(CampoPersonalizado)
class CampoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'nombre', 'tipo', 'requerido')
    search_fields = ('nombre', 'pipeline__nombre')
    list_filter = ('pipeline', 'tipo')


@admin.register(ValorCampoSolicitud)
class ValorCampoSolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'campo', 'valor')
    search_fields = ('solicitud__codigo', 'campo__nombre')
    list_filter = ('solicitud', 'campo')


@admin.register(RequisitoTransicion)
class RequisitoTransicionAdmin(admin.ModelAdmin):
    list_display = ('transicion', 'requisito', 'obligatorio', 'mensaje_personalizado')
    list_filter = ('transicion', 'obligatorio')
    search_fields = ('transicion__nombre', 'requisito__nombre', 'mensaje_personalizado')


@admin.register(PermisoPipeline)
class PermisoPipelineAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'grupo', 'usuario', 'puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar', 'puede_admin')
    list_filter = ('pipeline', 'grupo', 'puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar', 'puede_admin')
    search_fields = ('pipeline__nombre', 'grupo__name', 'usuario__username')
    list_editable = ('puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar', 'puede_admin')


@admin.register(PermisoBandeja)
class PermisoBandejaAdmin(admin.ModelAdmin):
    list_display = ('etapa', 'grupo', 'usuario', 'puede_ver', 'puede_tomar', 'puede_devolver', 'puede_transicionar', 'puede_editar')
    list_filter = ('etapa', 'grupo', 'puede_ver', 'puede_tomar', 'puede_devolver', 'puede_transicionar', 'puede_editar')
    search_fields = ('etapa__nombre', 'grupo__name', 'usuario__username')
    list_editable = ('puede_ver', 'puede_tomar', 'puede_devolver', 'puede_transicionar', 'puede_editar')


@admin.register(CalificacionCampo)
class CalificacionCampoAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'campo', 'estado', 'usuario', 'fecha_modificacion', 'tiene_comentario')
    list_filter = ('estado', 'campo', 'fecha_creacion', 'fecha_modificacion')
    search_fields = ('solicitud__codigo', 'campo', 'usuario__username', 'comentario')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    list_per_page = 50
    
    def tiene_comentario(self, obj):
        return bool(obj.comentario and obj.comentario.strip())
    tiene_comentario.boolean = True
    tiene_comentario.short_description = 'Tiene Comentario'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitud', 'usuario')


@admin.register(SolicitudComentario)
class SolicitudComentarioAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'usuario', 'tipo', 'comentario_truncado', 'fecha_creacion', 'es_editado')
    list_filter = ('tipo', 'es_editado', 'fecha_creacion')
    search_fields = ('solicitud__codigo', 'usuario__username', 'comentario')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'es_editado')
    list_per_page = 50
    
    def comentario_truncado(self, obj):
        if len(obj.comentario) > 100:
            return obj.comentario[:100] + '...'
        return obj.comentario
    comentario_truncado.short_description = 'Comentario'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitud', 'usuario')


# ==========================================
# ADMINISTRACIÓN DEL COMITÉ DE CRÉDITO
# ==========================================

@admin.register(NivelComite)
class NivelComiteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    list_display_links = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('orden',)
    list_per_page = 25


@admin.register(UsuarioNivelComite)
class UsuarioNivelComiteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nivel', 'fecha_asignacion', 'activo')
    list_display_links = ('usuario',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'nivel__nombre')
    list_filter = ('nivel', 'activo', 'fecha_asignacion')
    ordering = ('nivel__orden', 'usuario__username')
    list_per_page = 25


@admin.register(ParticipacionComite)
class ParticipacionComiteAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'usuario', 'nivel', 'resultado', 'fecha_modificacion')
    list_display_links = ('solicitud',)
    search_fields = ('solicitud__codigo', 'usuario__username', 'comentario')
    list_filter = ('nivel', 'resultado', 'fecha_modificacion')
    ordering = ('-fecha_modificacion',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    list_per_page = 25
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitud', 'usuario', 'nivel')


@admin.register(SolicitudEscalamientoComite)
class SolicitudEscalamientoComiteAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'solicitado_por', 'nivel_solicitado', 'atendido', 'fecha_solicitud', 'fecha_atencion')
    list_display_links = ('solicitud',)
    search_fields = ('solicitud__codigo', 'solicitado_por__username', 'comentario')
    list_filter = ('nivel_solicitado', 'atendido', 'fecha_solicitud')
    ordering = ('-fecha_solicitud',)
    readonly_fields = ('fecha_solicitud', 'fecha_atencion')
    list_per_page = 25
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitud', 'solicitado_por', 'nivel_solicitado', 'atendido_por')
