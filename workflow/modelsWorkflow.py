from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone

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
    codigo = models.CharField(max_length=50, unique=True)
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

    def __str__(self):
        return f"{self.codigo} ({self.pipeline.nombre})"


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
