from django.db import models

# Create your models here.
class FormPago(models.Model):
    descripcion = models.CharField(max_length=100, null=True)
    codigo = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class Aseguradora(models.Model):
    descripcion = models.CharField(max_length=100, null=True)
    codigo = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
    

class PeriodoPago(models.Model):
    codigo = models.IntegerField(null=True)
    descripcion = models.CharField(max_length=100, null=True)
    periocidad = models.IntegerField(null=True)

    def __str__(self):
        return self.descripcion
         

class Cotizacion(models.Model):
    SEXO_OPCIONES = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]
    LICENCIA_OPCIONES = [
        ('NO', 'No'),
        ('SI', 'Si'),
    ]
     
    #Datos del cliente
    nombreCliente = models.CharField(max_length=100, null=True)
    cedulaCliente = models.CharField(max_length=10, null=True,default='')
    fechaNacimiento = models.DateField(null=True)
    edad = models.IntegerField(null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
    #Parametros de la Cotizacion
    patrono = models.CharField(max_length=255, null=True)
    patronoCodigo = models.IntegerField(null=True)
    vendedor = models.CharField(max_length=255, null=True)
    vendedorComision = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    formaPago = models.IntegerField(null=True)
    periodoPago = models.IntegerField(null=True, default=1)
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE, null=True)
    # Datos de la cotización
    fechaInicioPago = models.DateField(null=True)
    montoPrestamo = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tasaInteres = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    comiCierre = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    plazoPago = models.IntegerField(null=True)
    r_deseada = models.DecimalField(max_digits=5, decimal_places=2, null=True)
   # Datos seguro de auto
    financiaSeguro = models.BooleanField(default=False)
    mesesFinanciaSeguro = models.IntegerField(null=True,default=3)
    montoanualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    montoMensualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    cantPagosSeguro = models.IntegerField(null=True,default=12)
    # DATOS DEL AUTO
    #DATOS DE LA CONSULTA
    observaciones = models.TextField(null=True, blank=True)
    #DETALLES DEL DEUDOR
    tiempoServicio = models.CharField(max_length=255, null=True)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    nombreEmpresa = models.CharField(max_length=255, null=True)
    referenciasAPC = models.CharField(max_length=255, null=True)
    cartera = models.CharField(max_length=255, null=True)
    licencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI')
    posicion = models.CharField(max_length=255, null=True)
    perfilUniversitario = models.CharField(max_length=255, null=True)

