from django.db import models
from django.contrib.auth.models import User

# 🧠 CURSO PRINCIPAL
class Curso(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True)

    def __str__(self):
        return self.titulo


# 📚 MÓDULOS DEL CURSO
class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=200)
    orden = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.orden}. {self.titulo}"


# 🧩 TEMAS dentro de un módulo
class Tema(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='temas')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    orden = models.PositiveIntegerField(default=1)

    video_local = models.FileField(upload_to='videos/temas/', null=True, blank=True)
    video_youtube = models.URLField(null=True, blank=True)
    imagen = models.ImageField(upload_to='imagenes_tema/', null=True, blank=True)
    documento = models.FileField(upload_to='documentos_tema/', null=True, blank=True)

    def __str__(self):
        return f"{self.orden}. {self.titulo}"

    def save(self, *args, **kwargs):
        if self.video_youtube:
            import re
            match = re.search(r"(?:v=|embed/|youtu.be/)([a-zA-Z0-9_-]{11})", self.video_youtube)
            if match:
                self.video_youtube = f"https://www.youtube.com/embed/{match.group(1)}"
        super().save(*args, **kwargs)


# 📂 ARCHIVOS ADICIONALES
class ArchivoAdicional(models.Model):
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='archivos')
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='archivos/')

    def __str__(self):
        return self.nombre



# 📊 PROGRESO DE CURSO
class ProgresoCurso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    modulos_completados = models.ManyToManyField(Modulo, blank=True)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo}"


# ✅ PROGRESO POR TEMA
class ProgresoTema(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tema.titulo}"
