from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Sala(models.Model):
    """
    Modelo para representar las salas de trabajo disponibles para reservas.
    
    Attributes:
        nombre (str): Nombre de la sala (ej: "Sala de Reuniones A")
        ubicacion (str): Ubicación física de la sala (ej: "Piso 2, Edificio Principal")
        capacidad (int): Número máximo de personas que puede albergar
        foto (ImageField): Imagen de referencia de la sala
        estado (str): Estado actual de la sala (activa/inactiva)
        descripcion (str): Descripción adicional de la sala
        equipamiento (str): Equipamiento disponible en la sala
        created_at (datetime): Fecha de creación del registro
        updated_at (datetime): Fecha de última actualización
    """
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre único de la sala")
    ubicacion = models.CharField(max_length=200, help_text="Ubicación física de la sala")
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número máximo de personas que puede albergar"
    )
    foto = models.ImageField(
        upload_to='intranet/salas/',
        null=True,
        blank=True,
        help_text="Foto de referencia de la sala"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa',
        help_text="Estado actual de la sala"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción adicional de la sala"
    )
    equipamiento = models.TextField(
        blank=True,
        help_text="Equipamiento disponible (proyector, pizarra, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.ubicacion}"
    
    @property
    def esta_disponible(self):
        """Verifica si la sala está disponible para reservas"""
        return self.estado == 'activa'
    
    def get_reservas_activas(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene las reservas activas para esta sala en un rango de fechas
        
        Args:
            fecha_inicio (datetime): Fecha de inicio del rango
            fecha_fin (datetime): Fecha de fin del rango
            
        Returns:
            QuerySet: Reservas activas en el rango especificado
        """
        reservas = self.reserva_set.filter(estado='activa')
        
        if fecha_inicio:
            reservas = reservas.filter(fecha_fin__gt=fecha_inicio)
        
        if fecha_fin:
            reservas = reservas.filter(fecha_inicio__lt=fecha_fin)
            
        return reservas


class Reserva(models.Model):
    """
    Modelo para representar las reservas de salas.
    
    Attributes:
        sala (Sala): Sala reservada
        usuario_creador (User): Usuario que creó la reserva
        titulo (str): Título de la reunión
        descripcion (str): Descripción de la reunión
        fecha_inicio (datetime): Fecha y hora de inicio
        fecha_fin (datetime): Fecha y hora de fin
        estado (str): Estado de la reserva
        created_at (datetime): Fecha de creación
        updated_at (datetime): Fecha de última actualización
    """
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        help_text="Sala reservada"
    )
    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas_creadas',
        help_text="Usuario que creó la reserva"
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Título de la reunión"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción de la reunión"
    )
    fecha_inicio = models.DateTimeField(help_text="Fecha y hora de inicio")
    fecha_fin = models.DateTimeField(help_text="Fecha y hora de fin")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa',
        help_text="Estado de la reserva"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['sala', 'fecha_inicio', 'fecha_fin']),
            models.Index(fields=['usuario_creador', 'fecha_inicio']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.sala.nombre} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"
    
    def clean(self):
        """Validación personalizada para la reserva"""
        from django.core.exceptions import ValidationError
        
        # Verificar que la fecha de fin sea posterior a la de inicio
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        
        # Verificar que la sala esté disponible
        if not self.sala.esta_disponible:
            raise ValidationError("La sala no está disponible para reservas")
        
        # Verificar que no haya conflictos de horario (solo si es una nueva reserva o se está modificando)
        if self.pk is None or self.fecha_inicio != self._state.fields_cache.get('fecha_inicio'):
            conflictos = self.sala.get_reservas_activas(
                fecha_inicio=self.fecha_inicio,
                fecha_fin=self.fecha_fin
            ).exclude(pk=self.pk)
            
            if conflictos.exists():
                raise ValidationError("La sala ya está reservada en este horario")
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para incluir validaciones"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def duracion_minutos(self):
        """Calcula la duración de la reserva en minutos"""
        return int((self.fecha_fin - self.fecha_inicio).total_seconds() / 60)
    
    @property
    def esta_activa(self):
        """Verifica si la reserva está activa"""
        return self.estado == 'activa' and self.fecha_fin > timezone.now()
    
    def get_participantes(self):
        """Obtiene todos los participantes de la reserva"""
        return self.participante_set.all()
    
    def get_participantes_confirmados(self):
        """Obtiene los participantes que han confirmado asistencia"""
        return self.participante_set.filter(estado_asistencia='confirmado')
    
    def cancelar(self):
        """Cancela la reserva y notifica a los participantes"""
        self.estado = 'cancelada'
        self.save()
        # Aquí se enviaría la notificación de cancelación


class Participante(models.Model):
    """
    Modelo para representar los participantes de una reserva.
    
    Attributes:
        reserva (Reserva): Reserva a la que pertenece
        usuario (User): Usuario participante
        estado_asistencia (str): Estado de confirmación de asistencia
        fecha_invitacion (datetime): Fecha cuando fue invitado
        fecha_confirmacion (datetime): Fecha cuando confirmó asistencia
    """
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('declinado', 'Declinado'),
        ('asistio', 'Asistió'),
        ('no_asistio', 'No Asistió'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        help_text="Reserva a la que pertenece"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuario participante"
    )
    estado_asistencia = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        help_text="Estado de confirmación de asistencia"
    )
    fecha_invitacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        unique_together = ['reserva', 'usuario']
        ordering = ['fecha_invitacion']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.reserva.titulo}"
    
    def confirmar_asistencia(self):
        """Confirma la asistencia del participante"""
        self.estado_asistencia = 'confirmado'
        self.fecha_confirmacion = timezone.now()
        self.save()
    
    def declinar_asistencia(self):
        """Declina la asistencia del participante"""
        self.estado_asistencia = 'declinado'
        self.fecha_confirmacion = timezone.now()
        self.save()


class Notificacion(models.Model):
    """
    Modelo para rastrear las notificaciones enviadas.
    
    Attributes:
        reserva (Reserva): Reserva relacionada
        tipo (str): Tipo de notificación
        destinatario (User): Usuario destinatario
        email_enviado (str): Email al que se envió
        fecha_envio (datetime): Fecha de envío
        estado (str): Estado del envío
        error_mensaje (str): Mensaje de error si falló
    """
    
    TIPO_CHOICES = [
        ('invitacion', 'Invitación'),
        ('recordatorio', 'Recordatorio'),
        ('cancelacion', 'Cancelación'),
        ('modificacion', 'Modificación'),
    ]
    
    ESTADO_CHOICES = [
        ('enviado', 'Enviado'),
        ('error', 'Error'),
        ('pendiente', 'Pendiente'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        help_text="Reserva relacionada"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        help_text="Tipo de notificación"
    )
    destinatario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuario destinatario"
    )
    email_enviado = models.EmailField(help_text="Email al que se envió")
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        help_text="Estado del envío"
    )
    error_mensaje = models.TextField(
        blank=True,
        help_text="Mensaje de error si falló el envío"
    )
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.tipo} - {self.destinatario.get_full_name()} - {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}" 