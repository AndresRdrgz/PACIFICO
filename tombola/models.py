from django.db import models

# Create your models here.

class Celulares(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=20, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    class Meta:
        db_table = 'celulares'

    def __str__(self):
        return self.numero