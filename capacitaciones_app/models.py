from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# 🧠 CURSO PRINCIPAL
class Curso(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
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
    video_externo = models.TextField(
        "Embed o link de video externo",
        null=True,
        blank=True,
        help_text="Pega aquí un iframe o un link de Vimeo, OneDrive, Google Drive, etc."
    )
    imagen = models.ImageField(upload_to='imagenes_tema/', null=True, blank=True)
    documento = models.FileField(upload_to='documentos_tema/', null=True, blank=True)

    def __str__(self):
        return f"{self.orden}. {self.titulo}"

    def save(self, *args, **kwargs):
        # Solo procesar si es un link de YouTube (opcional)
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

# 🗣️ Feedback de usuarios (modelo independiente)
class Feedback(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='feedbacks')
    puntuacion = models.PositiveSmallIntegerField(
        'Calificación',
        choices=[(i, f"{i} ⭐") for i in range(1, 6)]
    )
    comentario = models.TextField('Comentario', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        unique_together = ('usuario', 'tema')

    def __str__(self):
        return f"{self.usuario.username} – {self.tema.titulo} ({self.puntuacion}⭐)"

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

# 📝 Quiz asociado a Módulo
class Quiz(models.Model):
    modulo = models.OneToOneField(Modulo, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    instrucciones = models.TextField(blank=True, null=True)
    portada = models.ImageField(upload_to='quiz_portadas/', null=True, blank=True)  # 🖼️ Portada del quiz


    def __str__(self):
        return f"Quiz de {self.modulo.titulo}"

# ❓ Preguntas del Quiz
class Pregunta(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='preguntas', on_delete=models.CASCADE)
    texto = models.TextField()
    puntaje = models.PositiveIntegerField(default=0)
    archivo = models.FileField(upload_to='archivos_preguntas/', null=True, blank=True)  # 📎 Archivo opcional

    def __str__(self):
        return self.texto


# 🔘 Opciones por pregunta
class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.texto} ({'Correcta' if self.es_correcta else 'Incorrecta'})"

# 🧑‍🎓 Respuestas del estudiante
class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(Opcion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.pregunta.texto}"

# 🎯 Resultado final del quiz
class ResultadoQuiz(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    puntaje = models.IntegerField()
    aprobado = models.BooleanField(default=False)
    fecha_realizacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.quiz.modulo.titulo}: {self.puntaje} puntos"
