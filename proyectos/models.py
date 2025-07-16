from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Proyecto(models.Model):
    """Model for QA testing projects"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Proyecto")
    descripcion = models.TextField(verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('pausado', 'Pausado'),
            ('completado', 'Completado'),
            ('cancelado', 'Cancelado'),
        ],
        default='activo',
        verbose_name="Estado"
    )
    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proyectos_creados',
        verbose_name="Creado por"
    )
    
    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_pruebas(self):
        return self.pruebas.count()
    
    @property
    def pruebas_pendientes(self):
        return self.pruebas.filter(resultado='pendiente').count()
    
    @property
    def pruebas_exitosas(self):
        return self.pruebas.filter(resultado='exitoso').count()
    
    @property
    def pruebas_fallidas(self):
        return self.pruebas.filter(resultado='fallido').count()
    
    @property
    def pruebas_revision(self):
        return self.pruebas.filter(resultado='solicitud_revision').count()

class Modulo(models.Model):
    """Model for project modules"""
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='modulos',
        verbose_name="Proyecto"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Módulo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['nombre']
        unique_together = ['proyecto', 'nombre']
    
    def __str__(self):
        return f"{self.proyecto.nombre} - {self.nombre}"

class Prueba(models.Model):
    """Model for test cases"""
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    RESULTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
        ('solicitud_revision', 'Solicitud de Revisión'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='pruebas',
        verbose_name="Proyecto"
    )
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name='pruebas',
        verbose_name="Módulo"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título del Test Case")
    descripcion = models.TextField(verbose_name="Descripción del Test Case")
    pasos_prueba = models.TextField(verbose_name="Pasos de la Prueba")
    resultado_esperado = models.TextField(verbose_name="Resultado Esperado")
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name="Prioridad"
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='pendiente',
        verbose_name="Resultado"
    )
    tester = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pruebas_asignadas',
        verbose_name="Tester"
    )
    desarrollador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pruebas_desarrollo',
        verbose_name="Desarrollador"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_ejecucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Ejecución")
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")
    comentarios = models.TextField(blank=True, verbose_name="Comentarios")
    resuelto = models.BooleanField(default=False, verbose_name="Resuelto")
    
    class Meta:
        verbose_name = "Prueba"
        verbose_name_plural = "Pruebas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.proyecto.nombre} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        # Auto-update resolved status based on resultado
        if self.resultado == 'exitoso':
            self.resuelto = True
        elif self.resultado == 'fallido':
            self.resuelto = False
        
        # Update execution date when resultado changes from pendiente
        if self.pk:
            old_instance = Prueba.objects.get(pk=self.pk)
            if old_instance.resultado == 'pendiente' and self.resultado != 'pendiente':
                self.fecha_ejecucion = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def tiene_archivos(self):
        """Check if the test case has attached files"""
        return self.archivos_adjuntos.exists()
    
    @property
    def total_archivos(self):
        """Get the total number of attached files"""
        return self.archivos_adjuntos.count()

class ArchivoAdjunto(models.Model):
    """Model for file attachments to test cases"""
    prueba = models.ForeignKey(
        Prueba,
        on_delete=models.CASCADE,
        related_name='archivos_adjuntos',
        verbose_name="Prueba"
    )
    archivo = models.FileField(
        upload_to='proyectos/pruebas/archivos/',
        verbose_name="Archivo",
        help_text="Screenshots, logs, o documentos relacionados con la prueba"
    )
    nombre_original = models.CharField(
        max_length=255,
        verbose_name="Nombre Original",
        help_text="Nombre original del archivo"
    )
    descripcion = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción opcional del archivo"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    subido_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Subido por"
    )
    
    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre_original} - {self.prueba.titulo}"
    
    @property
    def nombre_archivo(self):
        """Get the filename of the attached file"""
        return self.archivo.name.split('/')[-1]
    
    @property
    def extension(self):
        """Get the file extension"""
        return self.nombre_original.split('.')[-1].lower() if '.' in self.nombre_original else ''
    
    @property
    def es_imagen(self):
        """Check if the file is an image"""
        return self.extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    
    @property
    def icono_archivo(self):
        """Get the appropriate icon for the file type"""
        if self.es_imagen:
            return 'fas fa-image'
        elif self.extension == 'pdf':
            return 'fas fa-file-pdf'
        elif self.extension in ['doc', 'docx']:
            return 'fas fa-file-word'
        elif self.extension in ['txt', 'log']:
            return 'fas fa-file-alt'
        else:
            return 'fas fa-file'

class ProyectoUsuario(models.Model):
    """Model for project user invitations and roles"""
    ROL_CHOICES = [
        ('tester', 'Tester'),
        ('desarrollador', 'Desarrollador'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='usuarios_invitados',
        verbose_name="Proyecto"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proyectos_invitado',
        verbose_name="Usuario"
    )
    rol = models.CharField(
        max_length=15,
        choices=ROL_CHOICES,
        verbose_name="Rol"
    )
    fecha_invitacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Invitación")
    fecha_aceptacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aceptación")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Usuario del Proyecto"
        verbose_name_plural = "Usuarios del Proyecto"
        unique_together = ['proyecto', 'usuario']
        ordering = ['-fecha_invitacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.proyecto.nombre} ({self.get_rol_display()})"
