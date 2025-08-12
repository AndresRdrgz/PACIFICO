from django.contrib import admin
from .models import (
    ClienteEntrevista, ReferenciaPersonal, ReferenciaComercial, OtroIngreso, 
    OpcionDesplegable, CalificacionDocumentoBackoffice, ComentarioDocumentoBackoffice, 
    HistorialBackoffice, FormularioWeb
)
from .modelsWorkflow import (
    Pipeline, Etapa, SubEstado, TransicionEtapa, PermisoEtapa, Solicitud, 
    HistorialSolicitud, Requisito, RequisitoPipeline, RequisitoSolicitud, 
    CampoPersonalizado, ValorCampoSolicitud, RequisitoTransicion, PermisoPipeline, 
    PermisoBandeja, CalificacionCampo, SolicitudComentario, NivelComite, 
    UsuarioNivelComite, ParticipacionComite, SolicitudEscalamientoComite, 
    ReportePersonalizado, EjecucionReporte, NotaRecordatorio, ReconsideracionSolicitud,
    CatalogoPendienteAntesFirma, PendienteSolicitud, AgendaFirma, OrdenExpediente, 
    PlantillaOrdenExpediente
)
from .forms import SolicitudAdminForm

class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 1

class SubEstadoInline(admin.TabularInline):
    model = SubEstado
    extra = 1
    fk_name = 'pipeline'  # For Pipeline admin
    fields = ('etapa', 'nombre', 'orden', 'sla')
    ordering = ('orden',)

class SubEstadoEtapaInline(admin.TabularInline):
    model = SubEstado
    extra = 1
    fk_name = 'etapa'  # For Etapa admin
    fields = ('nombre', 'orden', 'sla')
    ordering = ('orden',)

class TransicionEtapaInline(admin.TabularInline):
    model = TransicionEtapa
    extra = 1

class RequisitoPipelineInline(admin.TabularInline):
    model = RequisitoPipeline
    extra = 1
    fields = ('requisito', 'obligatorio', 'tipo_prestamo_aplicable')
    list_display = ('requisito', 'obligatorio', 'tipo_prestamo_aplicable')

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
    list_display = ('id', 'etapa', 'nombre', 'orden', 'sla_horas', 'pipeline')
    search_fields = ('nombre', 'etapa__nombre', 'pipeline__nombre')
    list_filter = ('etapa', 'pipeline')
    list_editable = ('orden',)
    ordering = ('etapa', 'orden')
    fields = ('etapa', 'pipeline', 'nombre', 'orden', 'sla')
    
    def sla_horas(self, obj):
        return obj.sla_horas
    sla_horas.short_description = 'SLA'


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
    list_display = ('id', 'codigo', 'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a', 'entrevista_cliente', 'creada_via_api', 'api_source', 'fecha_creacion', 'fecha_ultima_actualizacion')
    search_fields = ('codigo', 'pipeline__nombre', 'entrevista_cliente__primer_nombre', 'entrevista_cliente__primer_apellido', 'entrevista_cliente__email', 'api_source')
    list_filter = ('pipeline', 'etapa_actual', 'subestado_actual', 'entrevista_cliente__tipo_producto', 'creada_via_api', 'api_source')
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
        ('API Externa', {
            'fields': ('creada_via_api', 'api_source', 'enlace_conversacion'),
            'classes': ('collapse',)
        }),
        ('Canal Digital', {
            'fields': ('cliente_nombre', 'cliente_cedula', 'cliente_telefono', 'cliente_email', 'producto_solicitado', 'monto_solicitado', 'sector'),
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
    list_display = ('id', 'pipeline', 'requisito', 'obligatorio', 'tipo_prestamo_aplicable')
    search_fields = ('pipeline__nombre', 'requisito__nombre')
    list_filter = ('pipeline', 'tipo_prestamo_aplicable', 'obligatorio')
    fields = ('pipeline', 'requisito', 'obligatorio', 'tipo_prestamo_aplicable')


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
        'requisito_solicitud', 'colored_estado', 'calificado_por', 
        'opcion_desplegable', 'fecha_calificacion', 'subsanado',
        # 'subsanado_por_oficial', 'pendiente_completado'  # Activar después de migration
    )
    list_filter = (
        'estado', 'fecha_calificacion', 'opcion_desplegable', 'subsanado',
        # 'subsanado_por_oficial', 'pendiente_completado'  # Activar después de migration
    )
    search_fields = (
        'requisito_solicitud__requisito__nombre', 
        'calificado_por__username',
        'requisito_solicitud__solicitud__id',
        'subsanado_por__username'
    )
    readonly_fields = ('fecha_calificacion', 'fecha_modificacion')
    ordering = ('-fecha_calificacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('requisito_solicitud', 'calificado_por', 'estado', 'opcion_desplegable')
        }),
        ('Subsanación (Backoffice)', {
            'fields': ('subsanado', 'subsanado_por', 'fecha_subsanado'),
            'classes': ('collapse',)
        }),
        # ('Flujo Oficial-Backoffice', {  # Activar después de migration
        #     'fields': ('subsanado_por_oficial', 'pendiente_completado'),
        #     'classes': ('collapse',)
        # }),
        ('Fechas del Sistema', {
            'fields': ('fecha_calificacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    # Agregar colores para mejor visualización
    def get_list_display_links(self, request, list_display):
        return ['requisito_solicitud']
    
    def requisito_solicitud(self, obj):
        return f"{obj.requisito_solicitud.requisito.nombre} (ID: {obj.requisito_solicitud.solicitud.id})"
    requisito_solicitud.short_description = 'Documento y Solicitud'
    
    def colored_estado(self, obj):
        from django.utils.html import format_html
        colors = {
            'bueno': 'green',
            'malo': 'red', 
            'pendiente': 'orange'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    colored_estado.short_description = 'Estado'
    
    # OPCIONAL: Suprimir warning de "unload is not allowed" en navegadores modernos
    # class Media:
    #     js = ('workflow/admin_fix.js',)  # Descomentar si quieres eliminar el warning


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


# ==========================================================
# ADMIN PARA PENDIENTES ANTES DE FIRMA
# ==========================================================

@admin.register(CatalogoPendienteAntesFirma)
class CatalogoPendienteAntesFirmaAdmin(admin.ModelAdmin):
    """
    Administración del catálogo de pendientes antes de firma
    """
    list_display = ('orden', 'nombre', 'activo', 'fecha_creacion', 'solicitudes_count')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
    list_editable = ('orden', 'activo')
    list_display_links = ('nombre',)  # Hacer el nombre clickeable en lugar del orden
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden', 'activo')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def solicitudes_count(self, obj):
        """Muestra cuántas solicitudes tienen este pendiente asignado"""
        count = obj.solicitudes_asignadas.count()
        return f"{count} solicitud{'es' if count != 1 else ''}"
    solicitudes_count.short_description = "Solicitudes Asignadas"
    
    actions = ['activar_pendientes', 'desactivar_pendientes']
    
    def activar_pendientes(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} pendiente(s) activado(s) correctamente.')
    activar_pendientes.short_description = "Activar pendientes seleccionados"
    
    def desactivar_pendientes(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} pendiente(s) desactivado(s) correctamente.')
    desactivar_pendientes.short_description = "Desactivar pendientes seleccionados"


class PendienteSolicitudInline(admin.TabularInline):
    """
    Inline para mostrar pendientes de una solicitud en el admin de Solicitud
    """
    model = PendienteSolicitud
    extra = 0
    readonly_fields = ('fecha_agregado', 'etapa_agregado', 'subestado_agregado', 'fecha_completado', 'fecha_ultima_modificacion')
    fields = ('pendiente', 'estado', 'agregado_por', 'fecha_agregado', 'completado_por', 'fecha_completado', 'notas')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pendiente', 'agregado_por', 'completado_por')


@admin.register(PendienteSolicitud)
class PendienteSolicitudAdmin(admin.ModelAdmin):
    """
    Administración de pendientes asignados a solicitudes
    """
    list_display = ('solicitud_codigo', 'pendiente_nombre', 'estado_display', 'agregado_por', 'fecha_agregado', 'completado_por', 'fecha_completado', 'tiempo_transcurrido_display')
    list_filter = ('estado', 'fecha_agregado', 'fecha_completado', 'etapa_agregado', 'subestado_agregado', 'pendiente__nombre')
    search_fields = ('solicitud__codigo', 'pendiente__nombre', 'agregado_por__username', 'completado_por__username', 'notas')
    ordering = ('-fecha_agregado',)
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('solicitud', 'pendiente', 'estado')
        }),
        ('Auditoría de Creación', {
            'fields': ('agregado_por', 'fecha_agregado', 'etapa_agregado', 'subestado_agregado')
        }),
        ('Auditoría de Finalización', {
            'fields': ('completado_por', 'fecha_completado'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('notas', 'fecha_ultima_modificacion', 'ultima_modificacion_por'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_agregado', 'fecha_completado', 'fecha_ultima_modificacion')
    
    def solicitud_codigo(self, obj):
        """Muestra el código de la solicitud"""
        return obj.solicitud.codigo
    solicitud_codigo.short_description = "Código Solicitud"
    solicitud_codigo.admin_order_field = 'solicitud__codigo'
    
    def pendiente_nombre(self, obj):
        """Muestra el nombre del pendiente"""
        return obj.pendiente.nombre
    pendiente_nombre.short_description = "Pendiente"
    pendiente_nombre.admin_order_field = 'pendiente__nombre'
    
    def estado_display(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'por_hacer': 'red',
            'haciendo': 'orange', 
            'listo': 'green'
        }
        color = colors.get(obj.estado, 'black')
        return f'<span style="color: {color}; font-weight: bold;">{obj.get_estado_display()}</span>'
    estado_display.short_description = "Estado"
    estado_display.allow_tags = True
    estado_display.admin_order_field = 'estado'
    
    def tiempo_transcurrido_display(self, obj):
        """Muestra el tiempo transcurrido de forma legible"""
        tiempo = obj.tiempo_transcurrido
        days = tiempo.days
        hours, remainder = divmod(tiempo.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    tiempo_transcurrido_display.short_description = "Tiempo Transcurrido"
    
    actions = ['marcar_como_listo', 'marcar_como_por_hacer', 'marcar_como_haciendo']
    
    def marcar_como_listo(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.estado != 'listo':
                obj.estado = 'listo'
                obj.completado_por = request.user
                obj.ultima_modificacion_por = request.user
                obj.save()
                updated += 1
        self.message_user(request, f'{updated} pendiente(s) marcado(s) como "Listo".')
    marcar_como_listo.short_description = "Marcar como Listo"
    
    def marcar_como_por_hacer(self, request, queryset):
        updated = queryset.update(estado='por_hacer', completado_por=None, fecha_completado=None)
        # Actualizar ultima_modificacion_por manualmente
        for obj in queryset:
            obj.ultima_modificacion_por = request.user
            obj.save(update_fields=['ultima_modificacion_por'])
        self.message_user(request, f'{updated} pendiente(s) marcado(s) como "Por Hacer".')
    marcar_como_por_hacer.short_description = "Marcar como Por Hacer"
    
    def marcar_como_haciendo(self, request, queryset):
        updated = queryset.update(estado='haciendo', completado_por=None, fecha_completado=None)
        # Actualizar ultima_modificacion_por manualmente
        for obj in queryset:
            obj.ultima_modificacion_por = request.user
            obj.save(update_fields=['ultima_modificacion_por'])
        self.message_user(request, f'{updated} pendiente(s) marcado(s) como "Haciendo".')
    marcar_como_haciendo.short_description = "Marcar como Haciendo"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitud', 'pendiente', 'agregado_por', 'completado_por', 'ultima_modificacion_por')


# Agregar el inline de pendientes al admin de Solicitud existente
try:
    # Intentar modificar el admin existente
    existing_admin = admin.site._registry.get(Solicitud)
    if existing_admin:
        if hasattr(existing_admin, 'inlines'):
            existing_admin.inlines.append(PendienteSolicitudInline)
        else:
            existing_admin.inlines = [PendienteSolicitudInline]
except Exception:
    pass  # Si hay algún problema, continuar sin modificar

# Bloque try/except existente para RequisitoSolicitud
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


@admin.register(ReconsideracionSolicitud)
class ReconsideracionSolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'solicitud',
        'numero_reconsideracion',
        'solicitada_por',
        'fecha_solicitud',
        'estado',
        'analizada_por',
        'fecha_analisis',
        'usar_nueva_cotizacion',
    )
    
    list_filter = (
        'estado',
        'usar_nueva_cotizacion',
        'fecha_solicitud',
        'fecha_analisis',
    )
    
    search_fields = (
        'solicitud__codigo',
        'solicitada_por__username',
        'solicitada_por__first_name',
        'solicitada_por__last_name',
        'analizada_por__username',
        'analizada_por__first_name',
        'analizada_por__last_name',
        'motivo',
    )
    
    readonly_fields = (
        'creado_en',
        'actualizado_en',
        'numero_reconsideracion',
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'solicitud',
                'numero_reconsideracion',
                'solicitada_por',
                'fecha_solicitud',
                'motivo',
            )
        }),
        ('Cotizaciones', {
            'fields': (
                'cotizacion_original',
                'cotizacion_nueva',
                'usar_nueva_cotizacion',
            ),
            'classes': ('collapse',),
        }),
        ('Estado y Análisis', {
            'fields': (
                'estado',
                'analizada_por',
                'fecha_analisis',
                'comentario_analisis',
            )
        }),
        ('Información de Consulta Anterior', {
            'fields': (
                'resultado_consulta_anterior',
                'comentario_consulta_anterior',
            ),
            'classes': ('collapse',),
        }),
        ('Metadatos', {
            'fields': (
                'creado_en',
                'actualizado_en',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'solicitud',
            'solicitada_por',
            'analizada_por',
            'cotizacion_original',
            'cotizacion_nueva'
        )
    
    def has_change_permission(self, request, obj=None):
        # Solo permitir cambios a usuarios con permisos específicos
        return request.user.is_superuser or request.user.groups.filter(name__in=['Administradores', 'Consulta']).exists()
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar reconsideraciones
        return request.user.is_superuser


# ==========================================================
# ADMIN PARA AGENDA DE FIRMA
# ==========================================================

@admin.register(AgendaFirma)
class AgendaFirmaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para AgendaFirma.
    Permite gestionar las citas de firma desde el panel de administración.
    """
    
    list_display = (
        'id',
        'solicitud_codigo_display',
        'cliente_nombre_display', 
        'fecha_hora_display',
        'lugar_firma_display',
        'creado_por',
        'tiene_pendientes_display',
        'fecha_creacion'
    )
    
    list_filter = (
        'lugar_firma',
        'fecha_hora',
        'creado_por',
        'fecha_creacion'
    )
    
    search_fields = (
        'solicitud__codigo',
        'solicitud__cliente__nombreCliente',
        'solicitud__cotizacion__nombreCliente',
        'solicitud__cliente__cedula',
        'solicitud__cotizacion__cedulaCliente',
        'comentarios'
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información de la Cita', {
            'fields': ('solicitud', 'fecha_hora', 'lugar_firma')
        }),
        ('Detalles', {
            'fields': ('comentarios',)
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ('-fecha_hora',)
    
    # Métodos personalizados para list_display
    def solicitud_codigo_display(self, obj):
        """Muestra el código de la solicitud"""
        return obj.solicitud.codigo if obj.solicitud else 'N/A'
    solicitud_codigo_display.short_description = 'Solicitud'
    solicitud_codigo_display.admin_order_field = 'solicitud__codigo'
    
    def cliente_nombre_display(self, obj):
        """Muestra el nombre del cliente"""
        return obj.cliente_nombre
    cliente_nombre_display.short_description = 'Cliente'
    
    def fecha_hora_display(self, obj):
        """Muestra la fecha y hora formateada"""
        return obj.fecha_hora.strftime('%d/%m/%Y %I:%M %p')
    fecha_hora_display.short_description = 'Fecha y Hora'
    fecha_hora_display.admin_order_field = 'fecha_hora'
    
    def lugar_firma_display(self, obj):
        """Muestra el lugar de firma legible"""
        return obj.lugar_firma_display
    lugar_firma_display.short_description = 'Lugar'
    lugar_firma_display.admin_order_field = 'lugar_firma'
    
    def tiene_pendientes_display(self, obj):
        """Indica si tiene pendientes activos"""
        if obj.tiene_pendientes:
            return "⚠️ Sí"
        return "✅ No"
    tiene_pendientes_display.short_description = 'Pendientes'
    
    # Acciones personalizadas
    actions = ['marcar_completadas', 'duplicar_citas']
    
    def marcar_completadas(self, request, queryset):
        """Acción para marcar citas como completadas (ejemplo)"""
        # Esta funcionalidad se puede expandir según necesidades futuras
        self.message_user(request, f'{queryset.count()} citas procesadas.')
    marcar_completadas.short_description = "Procesar citas seleccionadas"
    
    def duplicar_citas(self, request, queryset):
        """Acción para duplicar citas seleccionadas"""
        count = 0
        for cita in queryset:
            # Crear una nueva cita basada en la existente
            nueva_cita = AgendaFirma.objects.create(
                solicitud=cita.solicitud,
                fecha_hora=cita.fecha_hora,
                lugar_firma=cita.lugar_firma,
                comentarios=f"Duplicado de cita #{cita.id}: {cita.comentarios}",
                creado_por=request.user
            )
            count += 1
        self.message_user(request, f'{count} citas duplicadas exitosamente.')
    duplicar_citas.short_description = "Duplicar citas seleccionadas"


# --------------------------------------
# ADMIN - ORDEN DE EXPEDIENTE
# --------------------------------------

class OrdenExpedienteInline(admin.TabularInline):
    """Inline para mostrar orden de expediente en la solicitud"""
    model = OrdenExpediente
    extra = 0
    fields = ('seccion', 'nombre_documento', 'orden', 'tiene_documento', 'obligatorio', 'comentarios')
    readonly_fields = ('calificado_por', 'fecha_calificacion')
    ordering = ('seccion', 'orden')


@admin.register(OrdenExpediente)
class OrdenExpedienteAdmin(admin.ModelAdmin):
    """Administración de orden de expediente"""
    list_display = ('solicitud', 'seccion', 'nombre_documento', 'orden', 'tiene_documento', 'obligatorio', 'calificado_por', 'fecha_calificacion')
    list_filter = ('seccion', 'tiene_documento', 'obligatorio', 'calificado_por', 'fecha_calificacion')
    search_fields = ('solicitud__codigo', 'nombre_documento', 'seccion', 'comentarios')
    list_editable = ('orden', 'tiene_documento', 'obligatorio')
    readonly_fields = ('calificado_por', 'fecha_calificacion', 'creado_en', 'actualizado_en')
    
    fieldsets = (
        ('Información General', {
            'fields': ('solicitud', 'seccion', 'nombre_documento', 'orden')
        }),
        ('Estado del Documento', {
            'fields': ('tiene_documento', 'obligatorio', 'activo')
        }),
        ('Calificación', {
            'fields': ('calificado_por', 'fecha_calificacion', 'comentarios'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('solicitud', 'calificado_por')


@admin.register(PlantillaOrdenExpediente)
class PlantillaOrdenExpedienteAdmin(admin.ModelAdmin):
    """Administración de plantillas de orden de expediente"""
    list_display = ('pipeline', 'orden_seccion', 'seccion', 'nombre_documento', 'orden', 'obligatorio', 'activo', 'creado_por', 'creado_en')
    list_filter = ('pipeline', 'seccion', 'orden_seccion', 'obligatorio', 'activo', 'creado_por')
    search_fields = ('pipeline__nombre', 'nombre_documento', 'seccion', 'descripcion')
    list_editable = ('orden_seccion', 'orden', 'obligatorio', 'activo')
    readonly_fields = ('creado_por', 'creado_en', 'actualizado_en')
    
    fieldsets = (
        ('Información General', {
            'fields': ('pipeline', 'seccion', 'orden_seccion', 'nombre_documento', 'orden')
        }),
        ('Configuración', {
            'fields': ('obligatorio', 'activo', 'descripcion')
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asignar el usuario creador automáticamente"""
        if not change:  # Si es nuevo objeto
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('pipeline', 'creado_por')
    
    actions = ['aplicar_plantillas_a_solicitudes']
    
    def aplicar_plantillas_a_solicitudes(self, request, queryset):
        """Aplicar plantillas seleccionadas a todas las solicitudes del pipeline"""
        count = 0
        for plantilla in queryset:
            # Buscar solicitudes del mismo pipeline que no tengan este documento
            solicitudes_pipeline = Solicitud.objects.filter(
                pipeline=plantilla.pipeline
            ).exclude(
                orden_expediente__seccion=plantilla.seccion,
                orden_expediente__orden=plantilla.orden
            )
            
            for solicitud in solicitudes_pipeline:
                OrdenExpediente.objects.create(
                    solicitud=solicitud,
                    seccion=plantilla.seccion,
                    nombre_documento=plantilla.nombre_documento,
                    orden=plantilla.orden,
                    obligatorio=plantilla.obligatorio
                )
                count += 1
                
        self.message_user(request, f'Plantillas aplicadas a {count} solicitudes.')
    aplicar_plantillas_a_solicitudes.short_description = "Aplicar plantillas a solicitudes del pipeline"


# --------------------------------------
# HISTORIAL BACK OFFICE ADMIN
# --------------------------------------

class SubsanadoFilter(admin.SimpleListFilter):
    """Filtro personalizado para eventos de subsanado"""
    title = 'Eventos de Subsanado'
    parameter_name = 'es_subsanado'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Sí - Eventos de Subsanado'),
            ('no', 'No - Otros Eventos'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(
                tipo_evento='calificacion',
                observaciones__icontains='SUBSANADO'
            )
        elif self.value() == 'no':
            return queryset.exclude(
                tipo_evento='calificacion',
                observaciones__icontains='SUBSANADO'
            )
        return queryset


@admin.register(HistorialBackoffice)
class HistorialBackofficeAdmin(admin.ModelAdmin):
    """
    Administración para el historial de Back Office con filtros avanzados
    """
    list_display = [
        'fecha_evento', 
        'solicitud_codigo', 
        'tipo_evento', 
        'usuario', 
        'evento_descripcion',
        'es_subsanado',
        'tiempo_formateado',
        'tiempo_bandeja_grupal_formateado'
    ]
    
    list_filter = [
        'tipo_evento',
        'fecha_evento',
        ('usuario', admin.RelatedOnlyFieldListFilter),
        ('usuario_asignado', admin.RelatedOnlyFieldListFilter),
        ('solicitud__pipeline', admin.RelatedOnlyFieldListFilter),
        ('solicitud__etapa_actual', admin.RelatedOnlyFieldListFilter),
        ('subestado_destino', admin.RelatedOnlyFieldListFilter),
        SubsanadoFilter,
    ]
    
    search_fields = [
        'solicitud__codigo',
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'usuario_asignado__username',
        'usuario_asignado__first_name',
        'usuario_asignado__last_name',
        'motivo_devolucion',
        'documento_nombre',
        'observaciones'
    ]
    
    readonly_fields = [
        'fecha_evento', 
        'tiempo_formateado',
        'tiempo_bandeja_grupal_formateado',
        'solicitud_link'
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': ('fecha_evento', 'tipo_evento', 'solicitud_link', 'usuario')
        }),
        ('Devolución', {
            'fields': ('motivo_devolucion',),
            'classes': ('collapse',),
        }),
        ('Cambio de Subestado', {
            'fields': (
                'subestado_origen', 
                'subestado_destino',
                'fecha_entrada_subestado',
                'fecha_salida_subestado',
                'tiempo_formateado'
            ),
            'classes': ('collapse',),
        }),
        ('Cambio de Calificación', {
            'fields': (
                'documento_nombre',
                'calificacion_anterior',
                'calificacion_nueva',
                'requisito_solicitud_id'
            ),
            'classes': ('collapse',),
        }),
        ('Eventos de Bandeja Grupal', {
            'fields': (
                'usuario_asignado',
                'fecha_entrada_bandeja_grupal',
                'fecha_asignacion_bandeja_grupal',
                'tiempo_bandeja_grupal_formateado'
            ),
            'classes': ('collapse',),
        }),
        ('Metadatos', {
            'fields': ('observaciones',),
            'classes': ('collapse',),
        }),
    )
    
    ordering = ['-fecha_evento']
    date_hierarchy = 'fecha_evento'
    
    def solicitud_codigo(self, obj):
        """Mostrar código de solicitud"""
        return obj.solicitud.codigo if obj.solicitud else "N/A"
    solicitud_codigo.short_description = 'Código Solicitud'
    solicitud_codigo.admin_order_field = 'solicitud__codigo'
    
    def evento_descripcion(self, obj):
        """Descripción resumida del evento"""
        if obj.tipo_evento == 'devolucion':
            return f"Devuelto por: {obj.motivo_devolucion[:50]}..." if obj.motivo_devolucion else "Devuelto"
        elif obj.tipo_evento == 'calificacion':
            descripcion = f"{obj.documento_nombre}: {obj.calificacion_anterior} -> {obj.calificacion_nueva}"
            # Agregar información de subsanado si está presente en las observaciones
            if obj.observaciones and 'SUBSANADO' in obj.observaciones:
                descripcion += " [SUBSANADO]"
            return descripcion
        elif obj.tipo_evento == 'subestado':
            origen = obj.subestado_origen.nombre if obj.subestado_origen else "Inicio"
            destino = obj.subestado_destino.nombre if obj.subestado_destino else "N/A"
            return f"{origen} -> {destino}"
        elif obj.tipo_evento == 'entrada_bandeja_grupal':
            subestado = obj.subestado_destino.nombre if obj.subestado_destino else "N/A"
            return f"Entrada a bandeja grupal: {subestado}"
        elif obj.tipo_evento == 'asignacion_desde_bandeja_grupal':
            usuario_asignado = obj.usuario_asignado.username if obj.usuario_asignado else "Usuario desconocido"
            subestado = obj.subestado_destino.nombre if obj.subestado_destino else "N/A"
            tiempo = obj.get_tiempo_bandeja_grupal_formateado() if obj.tiempo_en_bandeja_grupal else "N/A"
            return f"Asignado a {usuario_asignado} en {subestado} (Tiempo en bandeja: {tiempo})"
        return "N/A"
    evento_descripcion.short_description = 'Descripción del Evento'
    
    def es_subsanado(self, obj):
        """Indica si el evento es de subsanado"""
        if obj.tipo_evento == 'calificacion' and obj.observaciones:
            if 'SUBSANADO' in obj.observaciones:
                return "✅ Sí"
        return "❌ No"
    es_subsanado.short_description = 'Subsanado'
    es_subsanado.admin_order_field = 'observaciones'
    
    def tiempo_formateado(self, obj):
        """Tiempo en subestado formateado"""
        return obj.get_tiempo_formateado()
    tiempo_formateado.short_description = 'Tiempo en Subestado'
    
    def tiempo_bandeja_grupal_formateado(self, obj):
        """Tiempo en bandeja grupal formateado"""
        return obj.get_tiempo_bandeja_grupal_formateado()
    tiempo_bandeja_grupal_formateado.short_description = 'Tiempo en Bandeja Grupal'
    
    def solicitud_link(self, obj):
        """Link a la solicitud"""
        if obj.solicitud:
            from django.urls import reverse
            from django.utils.html import format_html
            try:
                url = reverse('admin:modelsWorkflow_solicitud_change', args=[obj.solicitud.pk])
                return format_html('<a href="{}" target="_blank">{}</a>', url, obj.solicitud.codigo)
            except:
                return obj.solicitud.codigo
        return "N/A"
    solicitud_link.short_description = 'Solicitud'
    solicitud_link.allow_tags = True
    
    def has_add_permission(self, request):
        """Deshabilitar creación manual"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo lectura para preservar integridad del historial"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo super usuarios pueden eliminar historial"""
        return request.user.is_superuser
