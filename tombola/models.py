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
    
class Tombola(models.Model):
    fecha_evento = models.DateTimeField(blank=True, null=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'tombola'

    def __str__(self):
        return f"Tombola {self.id} - {self.nombre}"
    
class Boleto(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tombola = models.ForeignKey(Tombola, on_delete=models.CASCADE, related_name='boletos')
    canalOrigen = models.CharField(
        max_length=50,
        choices=[
            ('Formulario', 'Formulario'),
            ('Carga masiva', 'Carga masiva')
        ],
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'boleto'

    def __str__(self):
        return f"Boleto"
    
class FormularioTombola(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    celular = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    correo_electronico = models.EmailField(max_length=100, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    sector = models.CharField(
        max_length=100,
        choices=[
            ('Sector público', 'Sector público'),
            ('Empresa privada', 'Empresa privada'),
            ('Jubilado', 'Jubilado'),
            ('Independiente', 'Independiente')
        ],
        blank=True,
        null=True
    )
    salario = models.CharField(
        max_length=50,
        choices=[
            ('Menor a $850.00', 'Menor a $850.00'),
            ('Entre $850.00 y $1,000.00', 'Entre $850.00 y $1,000.00'),
            ('Mayor que $1,000.00 hasta $2,000.00', 'Mayor que $1,000.00 hasta $2,000.00'),
            ('Mayor a $2,000.00', 'Mayor a $2,000.00'),
            ('Menor a $600.00', 'Menor a $600.00'),
            ('Entre $600.00 y $850.00', 'Entre $600.00 y $850.00'),
        ],
        blank=True,
        null=True
    )
    garantia = models.BooleanField(default=False)
    es_cliente = models.BooleanField(default=False)
    producto_interesado = models.CharField(
        max_length=100,
        choices=[
            ('Préstamos personal', 'Préstamos personal'),
            ('Préstamo personal con garantía hipotecaria', 'Préstamo personal con garantía hipotecaria'),
            ('Préstamo de auto', 'Préstamo de auto'),
            ('Préstamo para independiente o microempresario', 'Préstamo para independiente o microempresario'),
        ],
        blank=True,
        null=True
    )
    dinero_a_solicitar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oficial = models.CharField(max_length=100, blank=True, null=True)
    autorizacion_apc = models.BooleanField(default=False)
    acepta_condiciones = models.BooleanField(default=False)

    class Meta:
        db_table = 'formulario_tombola'

    def __str__(self):
        return f"Formulario {self.nombre} {self.apellido}"