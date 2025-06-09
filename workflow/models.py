from django.db import models

# Create your models here.

class ClienteEntrevista(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_entrevista = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"
