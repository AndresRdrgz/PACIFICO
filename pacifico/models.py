from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    
class PruebaDario(models.Model):
    nombre = models.CharField(max_length=100, null=True)
    apellido = models.CharField(max_length=100, null=True)
    departamento = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.nombre
    

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
    OFICIAL_OPCIONES = [
        ('TAIRA DE OBALDIA', 'TAIRA DE OBALDIA'),
        ('GERALDINE RODRIGUEZ', 'GERALDINE RODRIGUEZ'),
        ('BLANCA VERGARA', 'BLANCA VERGARA'),
        ('MICHELLE SANTANA', 'MICHELLE SANTANA'),
        ('SHARLEN SAMANIEGO', 'SHARLEN SAMANIEGO'),
        ('ISIS BARRIA', 'ISIS BARRIA'),
        ('ILSA JIMÉNEZ', 'ILSA JIMÉNEZ'),
        ('MELISSA VEGA', 'MELISSA VEGA'),
        ('ESTEFANI FORD', 'ESTEFANI FORD'),
        ('CHARLEENE CARRERA', 'CHARLEENE CARRERA'),
        ('INISHELL MOSQUERA', 'INISHELL MOSQUERA'),
        ('JEMIMA CASTILLO', 'JEMIMA CASTILLO'),
        ('KENIA SIERRA', 'KENIA SIERRA'),
        ('YARINETH SANCHEZ', 'YARINETH SANCHEZ'),
        ('AMARELIS ALTAMIRANDA', 'AMARELIS ALTAMIRANDA'),
        ('DAVID ARAUZ', 'DAVID ARAUZ'),
        ('KRISTY KING', 'KRISTY KING'),
        ('YAJANIS CONCEPCIÓN', 'YAJANIS CONCEPCIÓN'),
        ('YEZKA AVILA', 'YEZKA AVILA'),
        ('MIGDALIA TEJEIRA', 'MIGDALIA TEJEIRA'),
        ('HANNY CISNEROS', 'HANNY CISNEROS'),
        ('YITZEL LÓPEZ', 'YITZEL LÓPEZ'),
        ('NELLY CAMAÑO', 'NELLY CAMAÑO'),
        ('DEYDA SALDAÑA', 'DEYDA SALDAÑA'),
        ('JAVIER CASTILLO', 'JAVIER CASTILLO'),
        ('ELINA DÍAZ', 'ELINA DÍAZ'),
        ('YARKELIS REYES', 'YARKELIS REYES'),
        ('STEPHANY SANDOVAL', 'STEPHANY SANDOVAL'),
        ('MARICRUZ ARMUELLES', 'MARICRUZ ARMUELLES'),
        ('LARISSA MARCIAGA', 'LARISSA MARCIAGA'),
        ('SHELUNSKA MASA', 'SHELUNSKA MASA'),
        ('ARGELIS GOMEZ', 'ARGELIS GOMEZ'),
        ('ROSMERY ANDRADE', 'ROSMERY ANDRADE'),

    ]
     
    
  
    CARTERA_OPCIONES = [
        ("CONTRALORÍA", "CONTRALORÍA"),
        ("EMP. CSS", "EMP. CSS"),
        ("AUTÓNOMAS", "AUTÓNOMAS"),
        ("ACP", "ACP"),
        ("JUBILADO CSS", "JUBILADO CSS"),
        ("EMP. PRIVADA", "EMP. PRIVADA"),
        ("JUBILADO DE LA ZONA", "JUBILADO DE LA ZONA"),
        ("JUBI ACTIVO CONTRALORIA", "JUBI ACTIVO CONTRALORIA"),
        ("JUBI ACTIVO CSS", "JUBI ACTIVO CSS"),
        ("JUBILADO CONTRALORIA", "JUBILADO CONTRALORIA"),
        ("JUBI ACTIVO AUTÓNOMA", "JUBI ACTIVO AUTÓNOMA"),
        ("JUBILADO RIESGOS PROF. CSS", "JUBILADO RIESGOS PROF. CSS"),
        ("INDEPENDIENTE", "INDEPENDIENTE"),
    ]
    SUCURSALES_OPCIONES = [
        ("2", "COLON"),
        ("4", "CASINO"),
        ("7", "DAVID"),
        ("8", "CHORRERA"),
        ("11", "SANTIAGO"),
        ("13", "CALLE 50"),
        ("16", "CHITRE"),
        ("17", "PENONOME"),
]
    REFERENCIAS_OPCIONES = [
        ("BUENAS", "BUENAS"),
        ("REGULARES", "REGULARES"),
        ("MALAS", "MALAS"),
        ("PESIMAS", "PESIMAS"),
        ("SIN REFERENCIAS", "SIN REFERENCIAS"),
    ]

    #Jubilado choices Si o No
    JUBILADO_CHOICES = [
        ('SI', 'Si'),
        ('NO', 'No'),
    ]

    #OFICIAL
    oficial = models.CharField(max_length=255, choices=OFICIAL_OPCIONES,null=True)
    sucursal = models.CharField(max_length=255, choices=SUCURSALES_OPCIONES,null=True)

    #Datos del cliente
    nombreCliente = models.CharField(max_length=100, null=True)
    cedulaCliente = models.CharField(max_length=10, null=True,default='')
    fechaNacimiento = models.DateField(null=True)
    edad = models.IntegerField(null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
    jubilado = models.CharField(max_length=10, choices=JUBILADO_CHOICES, default='NO')
    #Parametros de la Cotizacion
    patrono = models.CharField(max_length=255, null=True)
    patronoCodigo = models.IntegerField(null=True)
    vendedor = models.CharField(max_length=255, null=True, default='1 - SIN VENDEDOR')
    vendedorComision = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    formaPago = models.IntegerField(null=True)
    periodoPago = models.IntegerField(null=True, default=1)
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE, null=True)
    # Datos de la cotización
    fechaInicioPago = models.DateField(null=True)
    montoPrestamo = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tasaInteres = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    comiCierre = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=13)
    plazoPago = models.IntegerField(null=True)
    r_deseada = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=14)
   # Datos seguro de auto
    financiaSeguro = models.BooleanField(default=False)
    mesesFinanciaSeguro = models.IntegerField(null=True,default=0)
    montoanualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    montoMensualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    cantPagosSeguro = models.IntegerField(null=True,default=0)
    # DATOS DEL AUTO
    cashback = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    abono = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    abonoPorcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=0)
    marca = models.CharField(max_length=255, null=True)
    modelo = models.CharField(max_length=255, null=True)
    yearsFinanciamiento = models.IntegerField(null=True,default=1)
    #DATOS DE LA CONSULTA
    observaciones = models.TextField(null=True, blank=True)
    #DETALLES DEL DEUDOR
    tiempoServicio = models.CharField(max_length=255, null=True)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    nombreEmpresa = models.CharField(max_length=255, null=True)
    referenciasAPC = models.CharField(max_length=255, null=True, choices=REFERENCIAS_OPCIONES)
    cartera = models.CharField(max_length=255, null=True, choices=CARTERA_OPCIONES)
    licencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI')
    posicion = models.CharField(max_length=255, null=True)
    perfilUniversitario = models.CharField(max_length=255, null=True)
    #NIVEL DE ENDEUDAMIENTO - DEUDOR
    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)

    #RESULTADOS COTIZACION
    tasaEstimada = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    tasaBruta = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    r1 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    auxMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    wrkMontoLetra = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    calcComiCierreFinal = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    calcMontoNotaria = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    calcMontoTimbres = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    tablaTotalPagos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalFeci = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalInteres = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalMontoCapital = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    manejo_5porc = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    #SAVE FUNCTION
    NumeroCotizacion = models.IntegerField(null=True, blank=True, unique=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.NumeroCotizacion is None:
            last_cotizacion = Cotizacion.objects.all().order_by('NumeroCotizacion').last()
            if last_cotizacion and last_cotizacion.NumeroCotizacion is not None:
                self.NumeroCotizacion = last_cotizacion.NumeroCotizacion + 1
            else:
                self.NumeroCotizacion = 1
        super(Cotizacion, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.NumeroCotizacion} - {self.nombreCliente} - {self.cedulaCliente}"