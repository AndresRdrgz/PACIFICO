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
    OFICIAL_OPCIONES = [
    ("AMARELIS ALTAMIRANDA", "AMARELIS ALTAMIRANDA"),
    ("ANA TERESA BENITEZ", "ANA TERESA BENITEZ"),
    ("ARGELIS GÓMEZ", "ARGELIS GÓMEZ"),
    ("BLANCA VERGARA", "BLANCA VERGARA"),
    ("CHARLEENE CARRERA", "CHARLEENE CARRERA"),
    ("CHRISTELL GARCIA", "CHRISTELL GARCIA"),
    ("DEYDA SALDAÑA", "DEYDA SALDAÑA"),
    ("EILEEN ORTEGA", "EILEEN ORTEGA"),
    ("ELINA DÍAZ", "ELINA DÍAZ"),
    ("GLENDA QUINTERO", "GLENDA QUINTERO"),
    ("ILSA JIMÉNEZ", "ILSA JIMÉNEZ"),
    ("INISHELL MOSQUERA", "INISHELL MOSQUERA"),
    ("ISIS BARRIA", "ISIS BARRIA"),
    ("JEMIMA CASTILLO", "JEMIMA CASTILLO"),
    ("KENIA SIERRA", "KENIA SIERRA"),
    ("KRISTY KING", "KRISTY KING"),
    ("LARISSA MARCIAGA", "LARISSA MARCIAGA"),
    ("LISETH DEL CARMEN ZAPATA", "LISETH DEL CARMEN ZAPATA"),
    ("MARICRUZ ARMUELLES", "MARICRUZ ARMUELLES"),
    ("MELISSA VEGA", "MELISSA VEGA"),
    ("MIGDALIA TEJEIRA", "MIGDALIA TEJEIRA"),
    ("ROSEMERY ANDRADE", "ROSEMERY ANDRADE"),
    ("SHARLEN SAMANIEGO", "SHARLEN SAMANIEGO"),
    ("STEPHANY SANDOVAL", "STEPHANY SANDOVAL"),
    ("TAIRA DE OBALDIA", "TAIRA DE OBALDIA"),
    ("YAJANIS CONCEPCIÓN", "YAJANIS CONCEPCIÓN"),
    ("YARINETH SANCHEZ", "YARINETH SANCHEZ"),
    ("YARISBETH ARDINES", "YARISBETH ARDINES"),
    ("YARKELIS REYES", "YARKELIS REYES"),
    ("YASHEIKA HENRIQUEZ", "YASHEIKA HENRIQUEZ"),
    ("YEISHA VILLAMIL", "YEISHA VILLAMIL"),
    ("YEZKA AVILA", "YEZKA AVILA"),
    ("YITZEL LÓPEZ", "YITZEL LÓPEZ"),
    ("YULEISIS GONZÁLEZ", "YULEISIS GONZÁLEZ"),
]
     
    
    CARTERA_OPCIONES = [

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
    #OFICIAL
    oficial = models.CharField(max_length=255, choices=OFICIAL_OPCIONES,null=True)

    #Datos del cliente
    nombreCliente = models.CharField(max_length=100, null=True)
    cedulaCliente = models.CharField(max_length=10, null=True,default='')
    fechaNacimiento = models.DateField(null=True)
    edad = models.IntegerField(null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
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
    comiCierre = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    plazoPago = models.IntegerField(null=True)
    r_deseada = models.DecimalField(max_digits=5, decimal_places=2, null=True)
   # Datos seguro de auto
    financiaSeguro = models.BooleanField(default=False)
    mesesFinanciaSeguro = models.IntegerField(null=True,default=0)
    montoanualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    montoMensualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    cantPagosSeguro = models.IntegerField(null=True,default=0)
    # DATOS DEL AUTO
    #DATOS DE LA CONSULTA
    observaciones = models.TextField(null=True, blank=True)
    #DETALLES DEL DEUDOR
    tiempoServicio = models.CharField(max_length=255, null=True)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    nombreEmpresa = models.CharField(max_length=255, null=True)
    referenciasAPC = models.CharField(max_length=255, null=True)
    cartera = models.CharField(max_length=255, null=True, choices=CARTERA_OPCIONES)
    licencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI')
    posicion = models.CharField(max_length=255, null=True)
    perfilUniversitario = models.CharField(max_length=255, null=True)
    #NIVEL DE ENDEUDAMIENTO - DEUDOR
    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True)

