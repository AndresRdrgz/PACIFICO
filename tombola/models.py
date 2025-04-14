from django.db import models
from pacifico.models import Cliente

SEXO_OPCIONES = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]


# Create your models here.



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
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='boletos', blank=True, null=True)
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
        return f"Boleto {self.id} - Tombola {self.tombola.id} - Cliente {self.cliente} - CanalOrigen {self.canalOrigen}"
    
class FormularioTombola(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedulaCliente = models.CharField(max_length=255, null=True)
    celular = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    correo_electronico = models.EmailField(max_length=100, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
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
    tombola = models.ForeignKey(Tombola, on_delete=models.CASCADE, related_name='formularios', blank=True, null=True)

    class Meta:
        db_table = 'formulario_tombola'

    def __str__(self):
        return f"Formulario {self.nombre} {self.apellido}"

    
