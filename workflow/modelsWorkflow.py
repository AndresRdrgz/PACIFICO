from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

# --------------------------------------
# PIPELINE Y ETAPAS
# --------------------------------------

class Pipeline(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Etapa(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='etapas')
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField()
    sla = models.DurationField(help_text="SLA: Tiempo máximo en esta etapa")
    es_bandeja_grupal = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pipeline', 'orden')
        ordering = ['orden']

    def __str__(self):
        return f"{self.pipeline.nombre} - {self.nombre}"
    
    @property
    def sla_horas(self):
        """Retorna el SLA formateado en horas"""
        if not self.sla:
            return "0h"
        
        total_hours = self.sla.days * 24 + self.sla.seconds // 3600
        return f"{total_hours}h"


class SubEstado(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='subestados')
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='subestados', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('etapa', 'nombre')
        ordering = ['orden']

    def __str__(self):
        return f"{self.etapa.nombre} - {self.nombre}"


class TransicionEtapa(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='transiciones')
    etapa_origen = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='transiciones_salida')
    etapa_destino = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='transiciones_entrada')
    nombre = models.CharField(max_length=100)
    requiere_permiso = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pipeline', 'etapa_origen', 'etapa_destino')

    def __str__(self):
        return f"{self.etapa_origen.nombre} → {self.etapa_destino.nombre} ({self.nombre})"


class PermisoEtapa(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='permisos')
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='etapas_permitidas')
    puede_ver = models.BooleanField(default=True)
    puede_autoasignar = models.BooleanField(default=True)

    class Meta:
        unique_together = ('etapa', 'grupo')

    def __str__(self):
        return f"{self.grupo.name} - {self.etapa.nombre}"

# --------------------------------------
# SOLICITUD
# --------------------------------------

class Solicitud(models.Model):
    PRIORIDAD_CHOICES = [
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
    ]
    
    COMO_SE_ENTERO_CHOICES = [
        ('Sucursal', 'Sucursal'),
        ('Ventas externas', 'Ventas externas'),
        ('Telemercadeo', 'Telemercadeo'),
        ('Promoción', 'Promoción'),
        ('Feria', 'Feria'),
        ('Plan chispa', 'Plan chispa'),
        ('Carta de saldo', 'Carta de saldo'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.PROTECT)
    etapa_actual = models.ForeignKey(Etapa, on_delete=models.SET_NULL, null=True, blank=True)
    subestado_actual = models.ForeignKey(SubEstado, on_delete=models.SET_NULL, null=True, blank=True)
    creada_por = models.ForeignKey(User, related_name='solicitudes_creadas', on_delete=models.CASCADE)
    asignada_a = models.ForeignKey(User, related_name='solicitudes_asignadas', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    etiquetas_oficial = models.CharField(max_length=255, null=True, blank=True, help_text="Etiquetas separadas por coma para la oficial")
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, null=True, blank=True, help_text="Prioridad de la solicitud")
    
    # Relaciones con Cliente y Cotización
    cliente = models.ForeignKey('pacifico.Cliente', on_delete=models.CASCADE, related_name='solicitudes', null=True, blank=True)
    cotizacion = models.ForeignKey('pacifico.Cotizacion', on_delete=models.CASCADE, related_name='solicitudes', null=True, blank=True)
    
    # Motivo de la consulta
    motivo_consulta = models.TextField(blank=True, null=True, help_text="Motivo de la consulta o observaciones del cliente")
    
    # Cómo se enteró del servicio
    como_se_entero = models.CharField(max_length=50, choices=COMO_SE_ENTERO_CHOICES, null=True, blank=True, help_text="Cómo se enteró del servicio")
    
    # APC con Makito fields
    TIPO_DOCUMENTO_CHOICES = [
        ('cedula', 'Cédula'),
        ('pasaporte', 'Pasaporte'),
    ]
    
    APC_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado'),
        ('error', 'Error'),
    ]
    
    descargar_apc_makito = models.BooleanField(default=False, help_text="Indica si se debe descargar APC con Makito")
    apc_no_cedula = models.CharField(max_length=50, null=True, blank=True, help_text="Número de cédula o pasaporte para APC")
    apc_tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, null=True, blank=True, help_text="Tipo de documento para APC")
    apc_status = models.CharField(max_length=20, choices=APC_STATUS_CHOICES, default='pending', help_text="Estado del proceso APC con Makito")
    apc_fecha_solicitud = models.DateTimeField(null=True, blank=True, help_text="Fecha cuando se solicitó el APC")
    apc_fecha_inicio = models.DateTimeField(null=True, blank=True, help_text="Fecha cuando Makito inició el proceso")
    apc_fecha_completado = models.DateTimeField(null=True, blank=True, help_text="Fecha cuando se completó el proceso APC")
    apc_observaciones = models.TextField(blank=True, null=True, help_text="Observaciones del proceso APC")
    apc_archivo = models.FileField(upload_to='apc_files/', null=True, blank=True, help_text="Archivo APC generado por Makito")
    # Origen de la solicitud (para etiquetas distintivas)
    origen = models.CharField(max_length=100, blank=True, null=True, help_text="Origen de la solicitud (ej: Canal Digital, Presencial, etc.)")
    
    # Campos adicionales para solicitudes del canal digital
    cliente_nombre = models.CharField(max_length=200, blank=True, null=True, help_text="Nombre completo del cliente")
    cliente_cedula = models.CharField(max_length=50, blank=True, null=True, help_text="Cédula del cliente")
    cliente_telefono = models.CharField(max_length=20, blank=True, null=True, help_text="Teléfono del cliente")
    cliente_email = models.EmailField(blank=True, null=True, help_text="Email del cliente")
    producto_solicitado = models.CharField(max_length=100, blank=True, null=True, help_text="Producto de interés")
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Monto solicitado")
    propietario = models.ForeignKey(User, related_name='solicitudes_propias', on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario propietario de la solicitud")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")
    
    # Relación con entrevista de cliente
    entrevista_cliente = models.ForeignKey('workflow.ClienteEntrevista', on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes', help_text="Entrevista de cliente asociada a esta solicitud")

    def __str__(self):
        return f"{self.codigo} ({self.pipeline.nombre})"
    
    def generar_codigo(self):
        """
        Genera el código secuencial basado en el ID de la solicitud y el prefijo del pipeline
        Formato: {PIPELINE_PREFIX}-{ID}
        """
        if not self.id:
            return None
        
        # Obtener prefijo del pipeline (primeras 3 letras, sin espacios ni caracteres especiales)
        pipeline_nombre = self.pipeline.nombre
        # Limpiar el nombre del pipeline: remover espacios, caracteres especiales y convertir a mayúsculas
        pipeline_clean = re.sub(r'[^a-zA-Z0-9]', '', pipeline_nombre)
        pipeline_prefix = pipeline_clean[:3].upper()
        
        # Si no hay suficientes caracteres, usar el nombre completo
        if len(pipeline_prefix) < 3:
            pipeline_prefix = pipeline_clean.upper()
        
        # Generar código con formato: PREFIX-ID
        return f"{pipeline_prefix}-{self.id}"
    
    def save(self, *args, **kwargs):
        # Si no tiene código y ya tiene ID, generarlo
        if not self.codigo and self.id:
            self.codigo = self.generar_codigo()
        super().save(*args, **kwargs)
    
    @property
    def cliente_nombre_completo(self):
        """Obtiene el nombre del cliente de forma consistente"""
        # Acceder directamente al campo de la base de datos para evitar recursión
        nombre_directo = self.__dict__.get('cliente_nombre', None)
        if nombre_directo:
            return nombre_directo
        elif self.cotizacion and self.cotizacion.nombreCliente:
            return self.cotizacion.nombreCliente
        elif self.cliente and self.cliente.nombreCliente:
            return self.cliente.nombreCliente
        else:
            return ""  # Campo en blanco si no hay cliente
    
    @property
    def cliente_cedula_completa(self):
        """Obtiene la cédula del cliente de forma consistente"""
        # Acceder directamente al campo de la base de datos para evitar recursión
        cedula_directa = self.__dict__.get('cliente_cedula', None)
        if cedula_directa:
            return cedula_directa
        elif self.cotizacion and self.cotizacion.cedulaCliente:
            return self.cotizacion.cedulaCliente
        elif self.cliente and self.cliente.cedulaCliente:
            return self.cliente.cedulaCliente
        else:
            return ""  # Campo en blanco si no hay cédula
    
    # Mantener compatibilidad con propiedades existentes
    # @property
    # def cliente_nombre(self):
    #     """Alias para compatibilidad hacia atrás - NO usar en código nuevo"""
    #     return self.cliente_nombre_completo
    
    # @property  
    # def cliente_cedula(self):
    #     """Alias para compatibilidad hacia atrás - NO usar en código nuevo"""
    #     return self.cliente_cedula_completa
    
    @property
    def monto_formateado(self):
        """Obtiene el monto financiado formateado"""
        # Acceder directamente al campo de la base de datos para evitar recursión
        monto_directo = self.__dict__.get('monto_solicitado', None)
        if monto_directo:
            return f"$ {monto_directo:,.2f}"
        elif self.cotizacion and self.cotizacion.auxMonto2:
            return f"$ {self.cotizacion.auxMonto2:,.2f}"
        elif self.cotizacion and self.cotizacion.montoPrestamo:
            # Fallback to montoPrestamo if auxMonto2 is not available
            return f"$ {self.cotizacion.montoPrestamo:,.2f}"
        return "$ 0.00"
    
    @property
    def producto_descripcion(self):
        """Obtiene el tipo de producto"""
        # Acceder directamente al campo de la base de datos para evitar recursión
        producto_directo = self.__dict__.get('producto_solicitado', None)
        if producto_directo:
            return producto_directo
        elif self.cotizacion:
            if self.cotizacion.tipoPrestamo == 'auto':
                return "Auto"
            elif self.cotizacion.tipoPrestamo == 'personal':
                return "Préstamo Personal"
        return "N/A"
        


class HistorialSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='historial')
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    subestado = models.ForeignKey(SubEstado, on_delete=models.SET_NULL, null=True, blank=True)
    usuario_responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def sla_vencido(self):
        if not self.fecha_fin:
            return timezone.now() > self.fecha_inicio + self.etapa.sla
        return self.fecha_fin > self.fecha_inicio + self.etapa.sla

# --------------------------------------
# REQUISITOS CONFIGURABLES
# --------------------------------------

class Requisito(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class RequisitoPipeline(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='requisitos_pipeline')
    requisito = models.ForeignKey(Requisito, on_delete=models.CASCADE)
    obligatorio = models.BooleanField(default=True)

    class Meta:
        unique_together = ('pipeline', 'requisito')

    def __str__(self):
        return f"{self.pipeline.nombre} - {self.requisito.nombre}"


class RequisitoSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='requisitos')
    requisito = models.ForeignKey(Requisito, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='requisitos/', null=True, blank=True)
    cumplido = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('solicitud', 'requisito')

    def __str__(self):
        return f"{self.solicitud.codigo} - {self.requisito.nombre}"

# --------------------------------------
# CAMPOS PERSONALIZADOS DINÁMICOS
# --------------------------------------

class CampoPersonalizado(models.Model):
    TIPO_CAMPO = [
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('entero', 'Entero'),
        ('fecha', 'Fecha'),
        ('booleano', 'Sí/No'),
    ]

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='campos_personalizados')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CAMPO)
    requerido = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.pipeline.nombre})"


class ValorCampoSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='valores_personalizados')
    campo = models.ForeignKey(CampoPersonalizado, on_delete=models.CASCADE)

    valor_texto = models.TextField(blank=True, null=True)
    valor_numero = models.FloatField(blank=True, null=True)
    valor_entero = models.IntegerField(blank=True, null=True)
    valor_fecha = models.DateField(blank=True, null=True)
    valor_booleano = models.BooleanField(blank=True, null=True)

    class Meta:
        unique_together = ('solicitud', 'campo')

    def __str__(self):
        return f"{self.solicitud.codigo} - {self.campo.nombre}"

    def valor(self):
        return getattr(self, f"valor_{self.campo.tipo}", None)

# --------------------------------------
# COMENTARIOS SOLICITUD
# --------------------------------------

class SolicitudComentario(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('analista', 'Analista'),
    ]
    
    solicitud = models.ForeignKey('Solicitud', on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    es_editado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.solicitud.codigo}"
    
    def save(self, *args, **kwargs):
        if self.pk:  # If updating existing comment
            self.es_editado = True
        super().save(*args, **kwargs)
        
    def get_tiempo_transcurrido(self):
        """Return human-readable time elapsed since creation"""
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        diff = now - self.fecha_creacion
        
        if diff.days > 0:
            return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace unos segundos"


# --------------------------------------
# CALIFICACIÓN DE CAMPOS DE COMPLIANCE
# --------------------------------------

class CalificacionCampo(models.Model):
    """
    Modelo para guardar la calificación de campos de compliance por solicitud
    """
    ESTADO_CHOICES = [
        ('bueno', 'Bueno'),
        ('malo', 'Malo'),
        ('sin_calificar', 'Sin Calificar'),
    ]
    
    solicitud = models.ForeignKey('Solicitud', on_delete=models.CASCADE, related_name='calificaciones_campos')
    campo = models.CharField(max_length=50, help_text="Nombre del campo (nombre, cedula, monto, etc.)")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='sin_calificar')
    comentario = models.TextField(blank=True, null=True, help_text="Comentario sobre la calificación")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Usuario que realizó la calificación")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('solicitud', 'campo')
        ordering = ['-fecha_modificacion']
        verbose_name = "Calificación de Campo"
        verbose_name_plural = "Calificaciones de Campos"
        
    def __str__(self):
        return f"{self.solicitud.codigo} - {self.campo}: {self.get_estado_display()}"
    
    def get_estado_display_color(self):
        """Retorna el color CSS basado en el estado"""
        colors = {
            'bueno': '#28a745',
            'malo': '#dc3545', 
            'sin_calificar': '#6c757d'
        }
        return colors.get(self.estado, '#6c757d')
    
    def get_estado_icon(self):
        """Retorna el icono FontAwesome basado en el estado"""
        icons = {
            'bueno': 'fa-check',
            'malo': 'fa-times',
            'sin_calificar': 'fa-question'
        }
        return icons.get(self.estado, 'fa-question')


# --------------------------------------
# SISTEMA DE COMITÉ DE CRÉDITO
# --------------------------------------

class NivelComite(models.Model):
    """
    Define los distintos niveles jerárquicos que pueden participar en el comité
    """
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(help_text="Jerarquía (menor = más bajo)")
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Nivel de Comité"
        verbose_name_plural = "Niveles de Comité"
    
    def __str__(self):
        return f"{self.nombre} (Orden: {self.orden})"


class UsuarioNivelComite(models.Model):
    """
    Relaciona usuarios con niveles de comité
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nivel = models.ForeignKey(NivelComite, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones sobre esta asignación")
    
    class Meta:
        unique_together = ('usuario', 'nivel')
        verbose_name = "Usuario Nivel Comité"
        verbose_name_plural = "Usuarios Niveles Comité"
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.nivel.nombre}"


class ParticipacionComite(models.Model):
    """
    Registra la opinión de cada usuario que participa en una solicitud del comité
    """
    RESULTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('OBSERVACIONES', 'Alternativa'),
    ]
    
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='participaciones_comite')
    nivel = models.ForeignKey(NivelComite, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comentario = models.TextField()
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('solicitud', 'nivel', 'usuario')
        ordering = ['-fecha_modificacion']
        verbose_name = "Participación en Comité"
        verbose_name_plural = "Participaciones en Comité"
    
    def __str__(self):
        return f"{self.solicitud.codigo} - {self.usuario.get_full_name()} - {self.get_resultado_display()}"


class SolicitudEscalamientoComite(models.Model):
    """
    Permite registrar que un usuario sugiere participación de un nivel superior
    """
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='escalamientos_comite')
    solicitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='escalamientos_solicitados')
    nivel_solicitado = models.ForeignKey(NivelComite, on_delete=models.PROTECT)
    comentario = models.TextField()
    atendido = models.BooleanField(default=False)
    atendido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalamientos_atendidos')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = "Escalamiento de Comité"
        verbose_name_plural = "Escalamientos de Comité"
    
    def __str__(self):
        return f"{self.solicitud.codigo} - Escalamiento a {self.nivel_solicitado.nombre}"


# --------------------------------------
# GESTIÓN DE ACCESO A PIPELINES Y BANDEJAS
# --------------------------------------

class PermisoPipeline(models.Model):
    """
    Modelo para definir qué usuarios/grupos pueden acceder a un pipeline completo
    """
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='permisos_pipeline')
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='pipelines_permitidos', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pipelines_permitidos', null=True, blank=True)
    puede_ver = models.BooleanField(default=True, help_text="Puede ver el pipeline y sus solicitudes")
    puede_crear = models.BooleanField(default=False, help_text="Puede crear nuevas solicitudes en este pipeline")
    puede_editar = models.BooleanField(default=False, help_text="Puede editar solicitudes en este pipeline")
    puede_eliminar = models.BooleanField(default=False, help_text="Puede eliminar solicitudes en este pipeline")
    puede_admin = models.BooleanField(default=False, help_text="Puede administrar la configuración del pipeline")

    class Meta:
        unique_together = ('pipeline', 'grupo', 'usuario')
        verbose_name = "Permiso de Pipeline"
        verbose_name_plural = "Permisos de Pipeline"

    def __str__(self):
        if self.grupo:
            return f"{self.pipeline.nombre} - Grupo: {self.grupo.name}"
        elif self.usuario:
            return f"{self.pipeline.nombre} - Usuario: {self.usuario.username}"
        return f"{self.pipeline.nombre} - Sin asignar"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.grupo and not self.usuario:
            raise ValidationError("Debe especificar un grupo o un usuario")
        if self.grupo and self.usuario:
            raise ValidationError("No puede especificar tanto un grupo como un usuario")


class PermisoBandeja(models.Model):
    """
    Modelo para definir qué usuarios/grupos pueden acceder a bandejas específicas
    """
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='permisos_bandeja')
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='bandejas_permitidas', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bandejas_permitidas', null=True, blank=True)
    puede_ver = models.BooleanField(default=True, help_text="Puede ver las solicitudes en esta bandeja")
    puede_tomar = models.BooleanField(default=True, help_text="Puede tomar solicitudes de esta bandeja")
    puede_devolver = models.BooleanField(default=True, help_text="Puede devolver solicitudes a esta bandeja")
    puede_transicionar = models.BooleanField(default=True, help_text="Puede realizar transiciones desde esta bandeja")
    puede_editar = models.BooleanField(default=False, help_text="Puede editar solicitudes en esta bandeja")

    class Meta:
        unique_together = ('etapa', 'grupo', 'usuario')
        verbose_name = "Permiso de Bandeja"
        verbose_name_plural = "Permisos de Bandeja"

    def __str__(self):
        if self.grupo:
            return f"{self.etapa.nombre} - Grupo: {self.grupo.name}"
        elif self.usuario:
            return f"{self.etapa.nombre} - Usuario: {self.usuario.username}"
        return f"{self.etapa.nombre} - Sin asignar"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.grupo and not self.usuario:
            raise ValidationError("Debe especificar un grupo o un usuario")
        if self.grupo and self.usuario:
            raise ValidationError("No puede especificar tanto un grupo como un usuario")


# --------------------------------------
# REQUISITOS POR TRANSICIÓN
# --------------------------------------

class RequisitoTransicion(models.Model):
    """
    Modelo para definir qué requisitos son obligatorios para transiciones específicas
    """
    transicion = models.ForeignKey(TransicionEtapa, on_delete=models.CASCADE, related_name='requisitos_obligatorios')
    requisito = models.ForeignKey(Requisito, on_delete=models.CASCADE)
    obligatorio = models.BooleanField(default=True, help_text="Si es obligatorio para esta transición")
    mensaje_personalizado = models.TextField(blank=True, null=True, help_text="Mensaje personalizado para este requisito")

    class Meta:
        unique_together = ('transicion', 'requisito')
        verbose_name = "Requisito de Transición"
        verbose_name_plural = "Requisitos de Transición"

    def __str__(self):
        return f"{self.transicion} - {self.requisito.nombre} ({'Obligatorio' if self.obligatorio else 'Opcional'})"


@receiver(post_save, sender=Solicitud)
def generar_codigo_solicitud(sender, instance, created, **kwargs):
    """
    Signal para generar automáticamente el código de la solicitud después de ser creada
    """
    if created and not instance.codigo:
        # Generar el código usando el ID que ya fue asignado
        instance.codigo = instance.generar_codigo()
        # Guardar solo el código sin disparar el signal nuevamente
        Solicitud.objects.filter(id=instance.id).update(codigo=instance.codigo)
# --------------------------------------
# REPORTES PERSONALIZADOS
# --------------------------------------

class ReportePersonalizado(models.Model):
    """
    Modelo para guardar reportes personalizados creados por los usuarios
    """
    nombre = models.CharField(max_length=200, help_text="Nombre descriptivo del reporte")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción detallada del reporte")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes_personalizados')
    filtros_json = models.JSONField(default=dict, help_text="Filtros aplicados al reporte en formato JSON")
    campos_json = models.JSONField(default=list, help_text="Campos incluidos en el reporte en formato JSON")
    configuracion_json = models.JSONField(default=dict, help_text="Configuración adicional del reporte")
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    es_favorito = models.BooleanField(default=False, help_text="Marcar como favorito")
    es_publico = models.BooleanField(default=False, help_text="Compartir con otros usuarios del mismo grupo")
    veces_ejecutado = models.PositiveIntegerField(default=0, help_text="Contador de ejecuciones")
    ultima_ejecucion = models.DateTimeField(null=True, blank=True, help_text="Última vez que se ejecutó")
    
    # Grupos que pueden ver este reporte (si es público)
    grupos_compartidos = models.ManyToManyField(Group, blank=True, related_name='reportes_compartidos')
    
    class Meta:
        ordering = ['-fecha_modificacion']
        verbose_name = "Reporte Personalizado"
        verbose_name_plural = "Reportes Personalizados"
    
    def __str__(self):
        return f"{self.nombre} ({self.usuario.get_full_name()})"
    
    def marcar_ejecutado(self):
        """Actualiza los contadores de ejecución"""
        self.veces_ejecutado += 1
        self.ultima_ejecucion = timezone.now()
        self.save(update_fields=['veces_ejecutado', 'ultima_ejecucion'])
    
    def puede_ver(self, usuario):
        """Verifica si un usuario puede ver este reporte"""
        # El creador siempre puede ver
        if self.usuario == usuario:
            return True
        
        # Superusuarios pueden ver todo
        if usuario.is_superuser:
            return True
        
        # Si es público y el usuario está en los grupos compartidos
        if self.es_publico:
            usuario_grupos = set(usuario.groups.all())
            reporte_grupos = set(self.grupos_compartidos.all())
            return bool(usuario_grupos & reporte_grupos)
        
        return False
    
    def get_tipo_display(self):
        """Retorna el tipo de reporte basado en la configuración"""
        config = self.configuracion_json
        return config.get('tipo', 'General')


class EjecucionReporte(models.Model):
    """
    Modelo para guardar el historial de ejecuciones de reportes
    """
    reporte = models.ForeignKey(ReportePersonalizado, on_delete=models.CASCADE, related_name='ejecuciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    parametros_json = models.JSONField(default=dict, help_text="Parámetros usados en la ejecución")
    tiempo_ejecucion = models.FloatField(null=True, blank=True, help_text="Tiempo de ejecución en segundos")
    registros_resultantes = models.PositiveIntegerField(default=0, help_text="Número de registros en el resultado")
    exitosa = models.BooleanField(default=True, help_text="Si la ejecución fue exitosa")
    mensaje_error = models.TextField(blank=True, null=True, help_text="Mensaje de error si falló")
    
    class Meta:
        ordering = ['-fecha_ejecucion']
        verbose_name = "Ejecución de Reporte"
        verbose_name_plural = "Ejecuciones de Reportes"
    
    def __str__(self):
        status = "✓" if self.exitosa else "✗"
        return f"{status} {self.reporte.nombre} - {self.fecha_ejecucion.strftime('%d/%m/%Y %H:%M')}"

# --------------------------------------
# CONFIGURACIÓN DEL CANAL DIGITAL
# --------------------------------------

class ConfiguracionCanalDigital(models.Model):
    """
    Modelo para configurar el comportamiento del Canal Digital
    """
    nombre = models.CharField(max_length=100, default="Configuración Canal Digital")
    pipeline_por_defecto = models.ForeignKey(Pipeline, on_delete=models.PROTECT, related_name='configuraciones_canal_digital')
    etapa_por_defecto = models.ForeignKey(Etapa, on_delete=models.PROTECT, related_name='configuraciones_canal_digital')
    activo = models.BooleanField(default=True, help_text="Si esta configuración está activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración Canal Digital"
        verbose_name_plural = "Configuraciones Canal Digital"
        ordering = ['-fecha_modificacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.pipeline_por_defecto.nombre}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Verificar que la etapa pertenece al pipeline
        if self.etapa_por_defecto and self.pipeline_por_defecto:
            if self.etapa_por_defecto.pipeline != self.pipeline_por_defecto:
                raise ValidationError('La etapa debe pertenecer al pipeline seleccionado')
    
    @classmethod
    def get_configuracion_activa(cls):
        """Obtiene la configuración activa del Canal Digital"""
        return cls.objects.filter(activo=True).first()
    
    @classmethod
    def get_pipeline_por_defecto(cls):
        """Obtiene el pipeline por defecto"""
        config = cls.get_configuracion_activa()
        if config:
            return config.pipeline_por_defecto
        # Fallback al primer pipeline disponible
        return Pipeline.objects.first()
    
    @classmethod
    def get_etapa_por_defecto(cls):
        """Obtiene la etapa por defecto"""
        config = cls.get_configuracion_activa()
        if config:
            return config.etapa_por_defecto
        # Fallback a la primera etapa del pipeline por defecto
        pipeline = cls.get_pipeline_por_defecto()
        if pipeline:
            return pipeline.etapas.first()
        return None
