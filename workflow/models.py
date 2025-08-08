from django.db import models
from .modelsWorkflow import *

# --- CHOICES GLOBALS ---
SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
]

PROVINCIA_CHOICES = [
    ('', '—'),  # Opción vacía con raya
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
]

LETRA_CEDULA_CHOICES = [
    ('', '—'),  # Opción vacía con raya
    ('E', 'E'),
    ('N', 'N'),
    ('PE', 'PE'),
    ('AV', 'AV'),
]

PRODUCTO_CHOICES = [
    ('Auto', 'Auto'),
    ('Personal', 'Personal'),
    ('Hipotecario', 'Hipotecario'),
]

NIVEL_ACADEMICO_CHOICES = [
    ('PRIMARIA', 'PRIMARIA'),
    ('SECUNDARIA', 'SECUNDARIA'),
    ('TECNICO', 'TECNICO'),
    ('UNIVERSITARIA', 'UNIVERSITARIA'),
    ('POST GRADO', 'POST GRADO'),
    ('MAESTRIA', 'MAESTRIA'),
    ('OTROS', 'OTROS'),
]

ORIGEN_FONDOS_CHOICES = [
    ('LOCAL', 'LOCAL'),
    ('EXTRANJERO', 'EXTRANJERO'),
]

# --- MODELOS ---
class ClienteEntrevista(models.Model):
    # DATOS GENERALES
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    provincia_cedula = models.CharField(max_length=2, choices=PROVINCIA_CHOICES, blank=True, null=True)
    tipo_letra = models.CharField(max_length=5, choices=LETRA_CEDULA_CHOICES, blank=True, null=True)
    tomo_cedula = models.CharField(max_length=10)
    partida_cedula = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    jubilado = models.BooleanField(default=False)
    nivel_academico = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Valores separados por coma para selección múltiple. Ej: PRIMARIA,SECUNDARIA",
    )
    
    lugar_nacimiento = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)
    no_dependientes = models.PositiveIntegerField(default=0)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_producto = models.CharField(max_length=50, choices=PRODUCTO_CHOICES)
    oficial = models.CharField(max_length=100)
    apellido_casada = models.CharField(max_length=100, blank=True, null=True)
    peso = models.DecimalField("Peso (lb)", max_digits=5, decimal_places=2, blank=True, null=True)
    estatura = models.DecimalField("Estatura (m)", max_digits=4, decimal_places=2, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, default="Panamá")
    ESTADO_CIVIL_CHOICES = [
        ('CASADO (A)', 'CASADO (A)'),
        ('UNIDO (A)', 'UNIDO (A)'),
        ('SOLTERO (A)', 'SOLTERO (A)'),
        ('VIUDO (A)', 'VIUDO (A)'),
        ('SEPARADO (A)', 'SEPARADO (A)'),
    ]
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)

    # DIRECCIÓN RESIDENCIAL
    direccion_completa = models.TextField(blank=True, null=True)
    barrio = models.CharField(max_length=100, blank=True, null=True)
    calle = models.CharField(max_length=100, blank=True, null=True)
    casa_apto = models.CharField(max_length=100, blank=True, null=True)

    # CÓNYUGE
    conyuge_nombre = models.CharField(max_length=100, blank=True, null=True)
    conyuge_cedula = models.CharField(max_length=15, blank=True, null=True)
    conyuge_lugar_trabajo = models.CharField(max_length=100, blank=True, null=True)
    conyuge_cargo = models.CharField(max_length=100, blank=True, null=True)
    conyuge_ingreso = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    conyuge_telefono = models.CharField(max_length=20, blank=True, null=True)

    # INFORMACIÓN LABORAL
    trabajo_direccion = models.TextField(blank=True, null=True)
    trabajo_lugar = models.CharField(max_length=100, blank=True, null=True)
    trabajo_cargo = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    TIPO_TRABAJO_CHOICES = [
        ('ASALARIADO', 'ASALARIADO'),
        ('INDEPENDIENTE', 'INDEPENDIENTE'),
        ('ABOGADO', 'ABOGADO'),
    ]
    tipo_trabajo = models.CharField(max_length=20, choices=TIPO_TRABAJO_CHOICES, blank=True, null=True)
    FRECUENCIA_PAGO_CHOICES = [
        ('SEMANAL', 'SEMANAL'),
        ('QUINCENAL', 'QUINCENAL'),
        ('MENSUAL', 'MENSUAL'),
    ]
    frecuencia_pago = models.CharField(max_length=20, choices=FRECUENCIA_PAGO_CHOICES, blank=True, null=True)
    tel_trabajo = models.CharField(max_length=10, blank=True, null=True)
    tel_ext = models.CharField(max_length=5, blank=True, null=True)
    origen_fondos = models.CharField(max_length=20, choices=ORIGEN_FONDOS_CHOICES, blank=True, null=True)
    fecha_inicio_trabajo = models.DateField(blank=True, null=True)

    # OTROS INGRESOS
    tipo_ingreso_1 = models.CharField(max_length=100, blank=True, null=True)
    descripcion_ingreso_1 = models.CharField(max_length=255, blank=True, null=True)
    monto_ingreso_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    tipo_ingreso_2 = models.CharField(max_length=100, blank=True, null=True)
    descripcion_ingreso_2 = models.CharField(max_length=255, blank=True, null=True)
    monto_ingreso_2 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    tipo_ingreso_3 = models.CharField(max_length=100, blank=True, null=True)
    descripcion_ingreso_3 = models.CharField(max_length=255, blank=True, null=True)
    monto_ingreso_3 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # PEP
    es_pep = models.BooleanField(default=False)
    pep_ingreso = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    pep_inicio = models.DateField(blank=True, null=True)
    pep_cargo_actual = models.CharField(max_length=100, blank=True, null=True)
    pep_fin = models.DateField(blank=True, null=True)
    pep_cargo_anterior = models.CharField(max_length=100, blank=True, null=True)
    pep_fin_anterior = models.DateField(blank=True, null=True)

    # PEP FAMILIAR
    es_familiar_pep = models.BooleanField(default=False)
    parentesco_pep = models.CharField(max_length=50, blank=True, null=True)
    nombre_pep = models.CharField(max_length=100, blank=True, null=True)
    cargo_pep = models.CharField(max_length=100, blank=True, null=True)
    institucion_pep = models.CharField(max_length=100, blank=True, null=True)
    pep_fam_inicio = models.DateField(blank=True, null=True)
    pep_fam_fin = models.DateField(blank=True, null=True)

    # DATOS BANCARIOS
    banco = models.CharField(max_length=100, blank=True, null=True)
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=20, blank=True, null=True)

    # AUTORIZACIONES
    autoriza_apc = models.BooleanField(default=False)
    acepta_datos = models.BooleanField(default=False)
    es_beneficiario_final = models.BooleanField(default=False)

    # SISTEMA
    fecha_entrevista = models.DateTimeField(auto_now_add=True)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    
    # ADMINISTRACIÓN
    completada_por_admin = models.BooleanField(default=False)
    fecha_completada_admin = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

    # Puedes agregar un método para mostrar los niveles académicos como lista
    def get_nivel_academico_list(self):
        if self.nivel_academico:
            return self.nivel_academico.split(',')
        return []


class ReferenciaPersonal(models.Model):
    entrevista = models.ForeignKey(
        ClienteEntrevista,
        on_delete=models.CASCADE,
        related_name='referencias_personales'
    )
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    relacion = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class ReferenciaComercial(models.Model):
    entrevista = models.ForeignKey(
        ClienteEntrevista,
        on_delete=models.CASCADE,
        related_name='referencias_comerciales'
    )
    TIPO_CHOICES = [
        ('', '---------'),
        ('COMERCIAL', 'COMERCIAL'),
        ('CLIENTES', 'CLIENTES'),
    ]
    tipo = models.CharField(max_length=100, choices=TIPO_CHOICES, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)  # <--- Cambiado aquí
    actividad = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    saldo = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nombre


class OtroIngreso(models.Model):
    cliente = models.ForeignKey(
        ClienteEntrevista,
        related_name='otros_ingresos',
        on_delete=models.CASCADE
    )
    TIPO_INGRESO_CHOICES = [
        ('', '---------'),
        ('LOCAL', 'LOCAL'),
        ('EXTRANJERO', 'EXTRANJERO'),
    ]
    tipo_ingreso = models.CharField(
        max_length=20,
        choices=TIPO_INGRESO_CHOICES,
        default='',
        blank=True,
        null=True
    )
    fuente = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.fuente
    def __str__(self):
        return self.fuente
        return self.fuente
    def __str__(self):
        return self.fuente


# ==========================================
# MODELO PARA FORMULARIO WEB CANAL DIGITAL
# ==========================================

# Importamos las opciones desde pacifico
from pacifico.models import OFICIAL_OPCIONES

SEXO_FORMULARIO_CHOICES = [
    ('MASCULINO', 'Masculino'),
    ('FEMENINO', 'Femenino'),
]

SECTOR_CHOICES = [
    ('Sector público', 'Sector público'),
    ('Empresa privada', 'Empresa privada'),
    ('Jubilado', 'Jubilado'),
    ('Independiente', 'Independiente')
]

SALARIO_CHOICES = [
    ('Menor a $600.00', 'Menor a $600.00'),
    ('Entre $600.00 y $850.00', 'Entre $600.00 y $850.00'),
    ('Menor a $850.00', 'Menor a $850.00'),
    ('Entre $850.00 y $1,000.00', 'Entre $850.00 y $1,000.00'),
    ('Mayor que $1,000.00 hasta $2,000.00', 'Mayor que $1,000.00 hasta $2,000.00'),
    ('Mayor a $2,000.00', 'Mayor a $2,000.00'),
]

PRODUCTO_INTERESADO_CHOICES = [
    ('Préstamos personal', 'Préstamos personal'),
    ('Préstamo de auto', 'Préstamo de auto'),
]

class FormularioWeb(models.Model):
    """Modelo para capturar solicitudes del formulario web del canal digital"""
    
    # Campos básicos
    nombre = models.CharField(max_length=100, verbose_name="Nombres")
    apellido = models.CharField(max_length=100, verbose_name="Apellidos")
    cedulaCliente = models.CharField(max_length=255, verbose_name="Cédula")
    celular = models.CharField(max_length=20, verbose_name="Celular")
    correo_electronico = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Correo Electrónico")
    
    # Información personal
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    edad = models.IntegerField(blank=True, null=True, verbose_name="Edad")
    sexo = models.CharField(
        max_length=10, 
        choices=SEXO_FORMULARIO_CHOICES, 
        default='MASCULINO',
        verbose_name="Sexo"
    )
    
    # Información laboral
    sector = models.CharField(
        max_length=100,
        choices=SECTOR_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sector"
    )
    
    salario = models.CharField(
        max_length=50,
        choices=SALARIO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Salario"
    )
    
    # Información del producto
    producto_interesado = models.CharField(
        max_length=100,
        choices=PRODUCTO_INTERESADO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Producto Interesado"
    )
    
    dinero_a_solicitar = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Dinero a Solicitar"
    )
    
    # Autorizaciones
    autorizacion_apc = models.BooleanField(
        default=False,
        verbose_name="Autorización APC"
    )
    acepta_condiciones = models.BooleanField(
        default=False,
        verbose_name="Acepta Condiciones"
    )
    
    # Campos de control
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True, 
        null=True,
        verbose_name="User Agent"
    )
    procesado = models.BooleanField(
        default=False,
        verbose_name="Procesado"
    )
    
    # Campo para asignar propietario del lead
    propietario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Propietario del Lead",
        help_text="Usuario asignado para gestionar este lead"
    )
    
    class Meta:
        db_table = 'workflow_formulario_web'
        verbose_name = 'Formulario Web'
        verbose_name_plural = 'Formularios Web'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedulaCliente}"
    
    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def get_salario_display_formatted(self):
        """Retorna el salario con formato amigable"""
        return self.get_salario_display() if self.salario else "No especificado"


# =============================================================================
# MODELOS PARA CALIFICACIÓN DE DOCUMENTOS
# =============================================================================

class OpcionDesplegable(models.Model):
    """Opciones predefinidas para el desplegable de calificación de documentos"""
    nombre = models.CharField(max_length=100, verbose_name="Opción")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_opcion_desplegable'
        verbose_name = 'Opción de Desplegable'
        verbose_name_plural = 'Opciones de Desplegable'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class CalificacionDocumentoBackoffice(models.Model):
    """Calificaciones de documentos por parte de analistas - Backoffice"""
    ESTADO_CHOICES = [
        ('bueno', 'Bueno'),
        ('malo', 'Malo'),
        ('pendiente', 'Pendiente'),
    ]
    
    requisito_solicitud = models.ForeignKey(
        'RequisitoSolicitud', 
        on_delete=models.CASCADE, 
        related_name='calificaciones_backoffice',
        verbose_name="Requisito de Solicitud"
    )
    calificado_por = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        verbose_name="Calificado por"
    )
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES, 
        verbose_name="Estado"
    )
    opcion_desplegable = models.ForeignKey(
        OpcionDesplegable, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Opción Seleccionada"
    )
    fecha_calificacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    subsanado = models.BooleanField(
        default=False, 
        verbose_name="Subsanado",
        help_text="Marca si el documento marcado como malo ha sido subsanado"
    )
    subsanado_por = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_subsanados_backoffice',
        verbose_name="Subsanado por"
    )
    fecha_subsanado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de subsanación"
    )
    
    # NUEVOS CAMPOS TEMPORALMENTE COMENTADOS HASTA EJECUTAR MIGRATION
    # subsanado_por_oficial = models.BooleanField(
    #     default=False,
    #     verbose_name="Subsanado por Oficial",
    #     help_text="Indica si la oficial ya subió/reemplazó el documento para subsanar el problema"
    # )
    # pendiente_completado = models.BooleanField(
    #     default=False,
    #     verbose_name="Pendiente Completado",
    #     help_text="Indica si la oficial ya subió archivo para un documento que estaba pendiente"
    # )
    
    class Meta:
        db_table = 'workflow_calificacion_documento_backoffice'
        verbose_name = 'Calificación de Documento - Backoffice'
        verbose_name_plural = 'Calificaciones de Documentos - Backoffice'
        ordering = ['-fecha_calificacion']
        # Un usuario solo puede tener una calificación activa por requisito
        unique_together = ['requisito_solicitud', 'calificado_por']
    
    def __str__(self):
        return f"{self.requisito_solicitud.requisito.nombre} - {self.get_estado_display()} por {self.calificado_por.username}"


class ComentarioDocumentoBackoffice(models.Model):
    """Comentarios sobre documentos - Backoffice"""
    requisito_solicitud = models.ForeignKey(
        'RequisitoSolicitud', 
        on_delete=models.CASCADE, 
        related_name='comentarios_backoffice',
        verbose_name="Requisito de Solicitud"
    )
    comentario_por = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        verbose_name="Comentario por"
    )
    comentario = models.TextField(verbose_name="Comentario")
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        db_table = 'workflow_comentario_documento_backoffice'
        verbose_name = 'Comentario de Documento - Backoffice'
        verbose_name_plural = 'Comentarios de Documentos - Backoffice'
        ordering = ['-fecha_comentario']
    
    def __str__(self):
        return f"Comentario en {self.requisito_solicitud.requisito.nombre} por {self.comentario_por.username}"


# --------------------------------------
# HISTORIAL BACK OFFICE
# --------------------------------------

class HistorialBackoffice(models.Model):
    """
    Historial completo de eventos en Back Office para trazabilidad y auditoría
    """
    
    TIPO_EVENTO_CHOICES = [
        ('devolucion', 'Devolución a Negocio'),
        ('calificacion', 'Cambio de Calificación'),
        ('subestado', 'Cambio de Subestado'),
        ('entrada_bandeja_grupal', 'Entrada a Bandeja Grupal'),
        ('asignacion_desde_bandeja_grupal', 'Asignación desde Bandeja Grupal'),
        ('solicitud_completa', 'Solicitud Marcada como Completa'),
    ]
    
    # Campos principales
    tipo_evento = models.CharField(
        max_length=35,  # ✅ CORREGIDO: Aumentado para cubrir 'asignacion_desde_bandeja_grupal' (31 chars)
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de Evento"
    )
    solicitud = models.ForeignKey(
        'workflow.Solicitud', 
        on_delete=models.CASCADE, 
        related_name='historial_backoffice',
        verbose_name="Solicitud"
    )
    usuario = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE,
        verbose_name="Usuario Responsable"
    )
    fecha_evento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Evento"
    )
    
    # Campos para DEVOLUCIÓN
    motivo_devolucion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Motivo de Devolución"
    )
    
    # Campos para CAMBIO DE SUBESTADO
    subestado_origen = models.ForeignKey(
        'workflow.SubEstado', 
        on_delete=models.CASCADE,
        related_name='historial_como_origen',
        blank=True, 
        null=True,
        verbose_name="Subestado Origen"
    )
    subestado_destino = models.ForeignKey(
        'workflow.SubEstado', 
        on_delete=models.CASCADE,
        related_name='historial_como_destino',
        blank=True, 
        null=True,
        verbose_name="Subestado Destino"
    )
    fecha_entrada_subestado = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Entrada al Subestado"
    )
    fecha_salida_subestado = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Salida del Subestado"
    )
    tiempo_en_subestado = models.DurationField(
        blank=True, 
        null=True,
        verbose_name="Tiempo en Subestado"
    )
    
    # Campos para CAMBIO DE CALIFICACIÓN
    documento_nombre = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Nombre del Documento"
    )
    calificacion_anterior = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Calificación Anterior"
    )
    calificacion_nueva = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Calificación Nueva"
    )
    requisito_solicitud_id = models.PositiveIntegerField(
        blank=True, 
        null=True,
        verbose_name="ID del Requisito de Solicitud"
    )
    
    # Campos para BANDEJA GRUPAL
    fecha_entrada_bandeja_grupal = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Entrada a Bandeja Grupal"
    )
    fecha_asignacion_bandeja_grupal = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Asignación desde Bandeja Grupal"
    )
    tiempo_en_bandeja_grupal = models.DurationField(
        blank=True, 
        null=True,
        verbose_name="Tiempo en Bandeja Grupal"
    )
    usuario_asignado = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE,
        related_name='asignaciones_backoffice',
        blank=True, 
        null=True,
        verbose_name="Usuario Asignado (para eventos de asignación)"
    )
    
    # Metadatos adicionales
    observaciones = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Observaciones Adicionales"
    )
    
    class Meta:
        db_table = 'workflow_historial_backoffice'
        verbose_name = 'Historial Back Office'
        verbose_name_plural = 'Historial Back Office'
        ordering = ['-fecha_evento']
        indexes = [
            models.Index(fields=['solicitud', 'tipo_evento']),
            models.Index(fields=['fecha_evento']),
            models.Index(fields=['usuario']),
        ]
    
    def __str__(self):
        if self.tipo_evento == 'devolucion':
            return f"Devolución #{self.solicitud.codigo} por {self.usuario.username}"
        elif self.tipo_evento == 'calificacion':
            return f"Calificación {self.documento_nombre} por {self.usuario.username}"
        elif self.tipo_evento == 'subestado':
            return f"Subestado {self.subestado_origen} → {self.subestado_destino} por {self.usuario.username}"
        elif self.tipo_evento == 'entrada_bandeja_grupal':
            return f"Entrada a bandeja grupal #{self.solicitud.codigo} en {self.subestado_destino}"
        elif self.tipo_evento == 'asignacion_desde_bandeja_grupal':
            usuario_asignado = self.usuario_asignado.username if self.usuario_asignado else "Usuario desconocido"
            return f"Asignación #{self.solicitud.codigo} a {usuario_asignado}"
        elif self.tipo_evento == 'solicitud_completa':
            return f"Solicitud #{self.solicitud.codigo} marcada como completa por {self.usuario.username}"
        return f"Evento {self.tipo_evento} por {self.usuario.username}"
    
    def get_tiempo_formateado(self):
        """Retorna el tiempo en subestado formateado"""
        if not self.tiempo_en_subestado:
            return "N/A"
        
        total_seconds = int(self.tiempo_en_subestado.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_tiempo_bandeja_grupal_formateado(self):
        """Retorna el tiempo en bandeja grupal formateado"""
        if not self.tiempo_en_bandeja_grupal:
            return "N/A"
        
        total_seconds = int(self.tiempo_en_bandeja_grupal.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

