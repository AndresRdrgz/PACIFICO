from django.contrib import admin
from .models import ClienteEntrevista, ReferenciaPersonal, ReferenciaComercial, OtroIngreso, OpcionDesplegable, CalificacionDocumentoBackoffice, ComentarioDocumentoBackoffice
from .modelsWorkflow import Pipeline, Etapa, SubEstado, TransicionEtapa, PermisoEtapa, Solicitud, HistorialSolicitud, Requisito, RequisitoPipeline, RequisitoSolicitud, CampoPersonalizado, ValorCampoSolicitud, RequisitoTransicion, PermisoPipeline, PermisoBandeja, CalificacionCampo, SolicitudComentario, NivelComite, UsuarioNivelComite, ParticipacionComite, SolicitudEscalamientoComite, ReportePersonalizado, EjecucionReporte, NotaRecordatorio
from .forms import SolicitudAdminForm

class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 1

class SubEstadoInline(admin.TabularInline):
    model = SubEstado
    extra = 1
    fk_name = 'pipeline'  # For Pipeline admin
    fields = ('etapa', 'nombre', 'orden')
    ordering = ('orden',)

class SubEstadoEtapaInline(admin.TabularInline):
    model = SubEstado
    extra = 1
    fk_name = 'etapa'  # For Etapa admin
    fields = ('nombre', 'orden')
    ordering = ('orden',)

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
    
    # Para facilitar la búsqueda en el autocomplete de Solicitud
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        return queryset, may_have_duplicates


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
    inlines = [EtapaInline, TransicionEtapaInline, RequisitoPipelineInline, CampoPersonalizadoInline]


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'nombre', 'orden', 'sla', 'es_bandeja_grupal')
    search_fields = ('nombre', 'pipeline__nombre')
    list_filter = ('pipeline',)
    inlines = [SubEstadoEtapaInline]


@admin.register(SubEstado)
class SubEstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'etapa', 'nombre', 'orden', 'pipeline')
    search_fields = ('nombre', 'etapa__nombre', 'pipeline__nombre')
    list_filter = ('etapa', 'pipeline')
    list_editable = ('orden',)
    ordering = ('etapa', 'orden')


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
    list_display = ('id', 'codigo', 'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a', 'entrevista_cliente', 'fecha_creacion', 'fecha_ultima_actualizacion')
    search_fields = ('codigo', 'pipeline__nombre', 'entrevista_cliente__primer_nombre', 'entrevista_cliente__primer_apellido', 'entrevista_cliente__email')
    list_filter = ('pipeline', 'etapa_actual', 'subestado_actual', 'entrevista_cliente__tipo_producto')
    autocomplete_fields = ('entrevista_cliente',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'pipeline', 'etapa_actual', 'subestado_actual')
        }),
        ('Asignación', {
            'fields': ('creada_por', 'asignada_a', 'propietario')
        }),
        ('Datos del Cliente', {
            'fields': ('cliente', 'cotizacion', 'entrevista_cliente')
        }),
        ('Información Adicional', {
            'fields': ('motivo_consulta', 'como_se_entero', 'prioridad', 'etiquetas_oficial', 'origen')
        }),
        ('Canal Digital', {
            'fields': ('cliente_nombre', 'cliente_cedula', 'cliente_telefono', 'cliente_email', 'producto_solicitado', 'monto_solicitado'),
            'classes': ('collapse',)
        }),
        ('APC Makito', {
            'fields': ('descargar_apc_makito', 'apc_no_cedula', 'apc_tipo_documento', 'apc_status', 'apc_fecha_solicitud', 'apc_fecha_inicio', 'apc_fecha_completado', 'apc_observaciones', 'apc_archivo'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )


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


# ==========================================
# ADMIN PARA FORMULARIO WEB CANAL DIGITAL
# ==========================================

from .models import FormularioWeb

@admin.register(FormularioWeb)
class FormularioWebAdmin(admin.ModelAdmin):
    """Administración para los formularios web del canal digital"""
    
    list_display = (
        'get_nombre_completo', 
        'cedulaCliente', 
        'celular', 
        'correo_electronico',
        'producto_interesado',
        'dinero_a_solicitar',
        'procesado',
        'fecha_creacion'
    )
    
    list_display_links = ('get_nombre_completo', 'cedulaCliente')
    
    search_fields = (
        'nombre', 
        'apellido', 
        'cedulaCliente', 
        'celular', 
        'correo_electronico'
    )
    
    list_filter = (
        'procesado',
        'sexo',
        'sector',
        'salario',
        'producto_interesado',
        'autorizacion_apc',
        'acepta_condiciones',
        'fecha_creacion'
    )
    
    readonly_fields = (
        'fecha_creacion', 
        'ip_address', 
        'user_agent'
    )
    
    fieldsets = (
        ('Información Personal', {
            'fields': (
                ('nombre', 'apellido'),
                'cedulaCliente',
                ('celular', 'correo_electronico'),
                ('fecha_nacimiento', 'sexo'),
            )
        }),
        ('Información Laboral', {
            'fields': (
                'sector',
                'salario',
            )
        }),
        ('Información del Producto', {
            'fields': (
                'producto_interesado',
                'dinero_a_solicitar',
            )
        }),
        ('Autorizaciones', {
            'fields': (
                'autorizacion_apc',
                'acepta_condiciones',
            )
        }),
        ('Control y Seguimiento', {
            'fields': (
                'procesado',
                'fecha_creacion',
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    
    actions = ['marcar_como_procesado', 'marcar_como_no_procesado', 'exportar_excel']
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'nombre'
    
    def marcar_como_procesado(self, request, queryset):
        """Marcar formularios seleccionados como procesados"""
        count = queryset.update(procesado=True)
        self.message_user(request, f'{count} formularios marcados como procesados.')
    marcar_como_procesado.short_description = 'Marcar como procesado'
    
    def marcar_como_no_procesado(self, request, queryset):
        """Marcar formularios seleccionados como no procesados"""
        count = queryset.update(procesado=False)
        self.message_user(request, f'{count} formularios marcados como no procesados.')
    marcar_como_no_procesado.short_description = 'Marcar como no procesado'
    
    def exportar_excel(self, request, queryset):
        """Exportar los formularios seleccionados a Excel"""
        # Esta función se puede implementar más adelante si se necesita
        self.message_user(request, 'Función de exportación en desarrollo.')
    exportar_excel.short_description = 'Exportar a Excel'
    
    def get_queryset(self, request):
        """Optimizar las consultas"""
        return super().get_queryset(request).select_related()
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar formularios"""
        return request.user.is_superuser
    
    def get_readonly_fields(self, request, obj=None):
        """Los campos de información personal son readonly después de creación"""
        readonly = list(self.readonly_fields)
        if obj:  # Si está editando (no creando)
            readonly.extend([
                'nombre', 'apellido', 'cedulaCliente', 'celular', 
                'correo_electronico', 'fecha_nacimiento', 'sexo',
                'sector', 'salario', 'producto_interesado', 
                'dinero_a_solicitar', 'autorizacion_apc', 'acepta_condiciones'
            ])
        return readonly


@admin.register(ReportePersonalizado)
class ReportePersonalizadoAdmin(admin.ModelAdmin):
    """Administración para los reportes personalizados"""
    
    list_display = (
        'nombre', 
        'usuario', 
        'es_favorito', 
        'es_publico',
        'veces_ejecutado',
        'fecha_modificacion'
    )
    
    list_display_links = ('nombre',)
    
    search_fields = (
        'nombre', 
        'descripcion', 
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name'
    )
    
    list_filter = (
        'es_favorito',
        'es_publico',
        'fecha_creacion',
        'fecha_modificacion'
    )
    
    readonly_fields = (
        'fecha_creacion', 
        'fecha_modificacion',
        'veces_ejecutado',
        'ultima_ejecucion'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre',
                'descripcion',
                'usuario',
            )
        }),
        ('Configuración', {
            'fields': (
                'filtros_json',
                'campos_json',
                'configuracion_json',
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': (
                'es_favorito',
                'es_publico',
                'grupos_compartidos',
                'veces_ejecutado',
                'ultima_ejecucion',
                'fecha_creacion',
                'fecha_modificacion',
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_modificacion',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(EjecucionReporte)
class EjecucionReporteAdmin(admin.ModelAdmin):
    """Administración para las ejecuciones de reportes"""
    
    list_display = (
        'reporte', 
        'usuario', 
        'exitosa',
        'registros_resultantes',
        'fecha_ejecucion',
        'tiempo_ejecucion'
    )
    
    list_display_links = ('reporte',)
    
    search_fields = (
        'reporte__nombre', 
        'usuario__username',
        'mensaje_error'
    )
    
    list_filter = (
        'exitosa',
        'fecha_ejecucion',
        'reporte'
    )
    
    readonly_fields = (
        'fecha_ejecucion',
        'tiempo_ejecucion',
        'registros_resultantes',
        'exitosa',
        'mensaje_error'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'reporte',
                'usuario',
                'exitosa',
            )
        }),
        ('Resultados', {
            'fields': (
                'registros_resultantes',
                'tiempo_ejecucion',
                'parametros_json',
            ),
            'classes': ('collapse',)
        }),
        ('Control', {
            'fields': (
                'fecha_ejecucion',
                'mensaje_error',
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'fecha_ejecucion'
    ordering = ('-fecha_ejecucion',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reporte', 'usuario')


# =============================================================================
# ADMINISTRACIÓN DE CALIFICACIÓN DE DOCUMENTOS
# =============================================================================

@admin.register(OpcionDesplegable)
class OpcionDesplegableAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'orden', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
    list_editable = ('orden', 'activo')


class ComentarioDocumentoInline(admin.TabularInline):
    model = ComentarioDocumentoBackoffice
    extra = 0
    readonly_fields = ('fecha_comentario', 'fecha_modificacion')
    fields = ('comentario_por', 'comentario', 'activo', 'fecha_comentario')


class CalificacionDocumentoInline(admin.TabularInline):
    model = CalificacionDocumentoBackoffice
    extra = 0
    readonly_fields = ('fecha_calificacion', 'fecha_modificacion')
    fields = ('calificado_por', 'estado', 'opcion_desplegable', 'fecha_calificacion')


@admin.register(CalificacionDocumentoBackoffice)
class CalificacionDocumentoBackofficeAdmin(admin.ModelAdmin):
    list_display = (
        'requisito_solicitud', 'calificado_por', 'estado', 
        'opcion_desplegable', 'fecha_calificacion'
    )
    list_filter = ('estado', 'fecha_calificacion', 'opcion_desplegable')
    search_fields = (
        'requisito_solicitud__requisito__nombre', 
        'calificado_por__username',
        'requisito_solicitud__solicitud__id'
    )
    readonly_fields = ('fecha_calificacion', 'fecha_modificacion')
    ordering = ('-fecha_calificacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('requisito_solicitud', 'calificado_por', 'estado', 'opcion_desplegable')
        }),
        ('Fechas', {
            'fields': ('fecha_calificacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComentarioDocumentoBackoffice)
class ComentarioDocumentoBackofficeAdmin(admin.ModelAdmin):
    list_display = (
        'requisito_solicitud', 'comentario_por', 'comentario_preview', 
        'activo', 'fecha_comentario'
    )
    list_filter = ('activo', 'fecha_comentario')
    search_fields = (
        'requisito_solicitud__requisito__nombre', 
        'comentario_por__username',
        'comentario',
        'requisito_solicitud__solicitud__id'
    )
    readonly_fields = ('fecha_comentario', 'fecha_modificacion')
    ordering = ('-fecha_comentario',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('requisito_solicitud', 'comentario_por', 'comentario', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_comentario', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def comentario_preview(self, obj):
        return obj.comentario[:50] + '...' if len(obj.comentario) > 50 else obj.comentario
    comentario_preview.short_description = 'Comentario'


# Agregar inlines a RequisitoSolicitudAdmin si existe
try:
    # Intentar encontrar el admin existente de RequisitoSolicitud
    from django.contrib.admin.sites import site
    if RequisitoSolicitud in site._registry:
        # Si ya existe, agregar nuestros inlines
        existing_admin = site._registry[RequisitoSolicitud]
        if hasattr(existing_admin, 'inlines'):
            existing_admin.inlines = list(existing_admin.inlines) + [CalificacionDocumentoInline, ComentarioDocumentoInline]
        else:
            existing_admin.inlines = [CalificacionDocumentoInline, ComentarioDocumentoInline]
except Exception:
    # Si no existe o hay algún problema, crear uno nuevo
    @admin.register(RequisitoSolicitud)
    class RequisitoSolicitudAdmin(admin.ModelAdmin):
        list_display = ('solicitud', 'requisito', 'cumplido', 'fecha_subida')
        list_filter = ('cumplido', 'fecha_subida')
        search_fields = ('solicitud__id', 'requisito__nombre')
        inlines = [CalificacionDocumentoInline, ComentarioDocumentoInline]


@admin.register(NotaRecordatorio)
class NotaRecordatorioAdmin(admin.ModelAdmin):
    """Administración para las notas y recordatorios"""
    
    list_display = (
        'id', 'solicitud', 'tipo', 'titulo', 'prioridad', 'estado', 
        'usuario', 'fecha_creacion', 'fecha_vencimiento', 'es_activo'
    )
    
    list_display_links = ('id', 'titulo')
    
    search_fields = (
        'titulo', 'contenido', 'solicitud__codigo', 
        'usuario__username', 'usuario__first_name', 'usuario__last_name'
    )
    
    list_filter = (
        'tipo', 'prioridad', 'estado', 'es_activo', 
        'fecha_creacion', 'fecha_vencimiento'
    )
    
    readonly_fields = (
        'fecha_creacion', 'fecha_modificacion'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'solicitud',
                'usuario',
                'tipo',
                'titulo',
                'contenido',
                'prioridad',
            )
        }),
        ('Recordatorio', {
            'fields': (
                'fecha_vencimiento',
                'estado',
            ),
            'classes': ('collapse',),
            'description': 'Campos específicos para recordatorios'
        }),
        ('Control', {
            'fields': (
                'es_activo',
                'fecha_creacion',
                'fecha_modificacion',
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'solicitud', 'usuario'
        )
