from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

SEXO_OPCIONES = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]

JUBILADO_CHOICES = [
        ('SI', 'Si'),
        ('NO', 'No'),
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
        ('ANDRES RODRIGUEZ', 'ANDRES RODRIGUEZ'),
        ('ODESSA TEJEIRA', 'ODESSA TEJEIRA'),
        ('JAVIER CASTILLO', 'JAVIER CASTILLO'),
        ('ROSA FRANCO', 'ROSA FRANCO'),
        ('YARISBETH ARDINES', 'YARISBETH ARDINES'),
        ('MELANIE CEDEÑO', 'MELANIE CEDEÑO'),
        ('YENIFFER MENESES', 'YENIFFER MENESES'),
        ('ISRAEL CARRERA', 'ISRAEL CARRERA'),
        ('LUIS SAMANIEGO', 'LUIS SAMANIEGO'),
        ('SCARLIN CONTRERAS', 'SCARLIN CONTRERAS'),
        ('MIGDALIA DE LEÓN', 'MIGDALIA DE LEÓN'),
        ('IVAN RICHARDS', 'IVAN RICHARDS'),

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

MESES_OPCIONES = [
    ('ENERO', 'ENERO'),
    ('FEBRERO', 'FEBRERO'),
    ('MARZO', 'MARZO'),
    ('ABRIL', 'ABRIL'),
    ('MAYO', 'MAYO'),
    ('JUNIO', 'JUNIO'),
    ('JULIO', 'JULIO'),
    ('AGOSTO', 'AGOSTO'),
    ('SEPTIEMBRE', 'SEPTIEMBRE'),
    ('OCTUBRE', 'OCTUBRE'),
    ('NOVIEMBRE', 'NOVIEMBRE'),
    ('DICIEMBRE', 'DICIEMBRE'),
    ]

TIPO_PRORRATEO_OPCIONES = [
        ('horas_extras', 'Horas Extras'),
        ('prima_produccion', 'Prima de Producción'),
    ]
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sucursal = models.CharField(max_length=255, choices=SUCURSALES_OPCIONES, null=True)
    oficial = models.CharField(max_length=255, choices=OFICIAL_OPCIONES, null=True)
    auto_save_cotizaciones = models.BooleanField(default=False)
    pruebaFuncionalidades = models.BooleanField(default=False)
    rol = models.CharField(
        max_length=20,
        choices=[('Oficial', 'Oficial'), ('Administrador', 'Administrador'), ('Supervisor', 'Supervisor')],
        default='Oficial'
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username
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
         

class Cliente(models.Model):
    cedulaCliente = models.CharField(max_length=255, null=True)
    
    nombreCliente = models.CharField(max_length=255, null=True)
    fechaNacimiento = models.DateField(null=True,blank=True)
    edad = models.IntegerField(null=True,blank=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
    jubilado = models.CharField(max_length=10, choices=JUBILADO_CHOICES, default='NO',blank=True,null=True)
    
    
    
    def __str__(self):
        return f"{self.nombreCliente} - {self.cedulaCliente}"
    


class Cotizacion(models.Model):
    
   
   
    #OFICIAL
    oficial = models.CharField(max_length=255, choices=OFICIAL_OPCIONES,null=True)
    sucursal = models.CharField(max_length=255, choices=SUCURSALES_OPCIONES,null=True)
    tipoPrestamo = models.CharField(
        max_length=20,
        choices=[('auto', 'Préstamo de Auto'), ('personal', 'Préstamo Personal')],
        default='',
        blank=True,
        null=True
    )
    #Datos del cliente
    nombreCliente = models.CharField(max_length=100, null=True)
    cedulaCliente = models.CharField(max_length=20, null=True,default='')
    tipoDocumento = models.CharField(max_length=10, choices=[('CEDULA', 'Cédula'), ('PASAPORTE', 'Pasaporte')], default='CEDULA')
    fechaNacimiento = models.DateField(null=True)
    edad = models.IntegerField(null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
    jubilado = models.CharField(max_length=10, choices=JUBILADO_CHOICES, default='NO')
    apcScaore = models.IntegerField(null=True,blank=True)
    apcPI = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
   
    #Parametros de la Cotizacion
    aplicaPromocion = models.BooleanField(default=False, blank=True, null=True)
    patrono = models.CharField(max_length=255, null=True)
    patronoCodigo = models.IntegerField(null=True)
    vendedor = models.CharField(max_length=255, null=True)
    vendedorComision = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    vendedorComisionPorcentaje = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    vendedorOtroPorcentaje = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    vendedorOtroComision = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    vendedorTipo = models.CharField(
        max_length=20,
        choices=[
            ('SIN VENDEDOR', 'SIN VENDEDOR'),
            ('EXTERNO', 'EXTERNO'),
            ('CHISPA', 'CHISPA'),
            ('INTERNO', 'INTERNO'),
            ('SATELITE', 'SATELITE'),
            ('AGENCIAS', 'AGENCIAS'),
        ],
        null=True,
        blank=True
    )
    #CANCELACION
    cancDescripcion1 = models.CharField(max_length=255, null=True, blank=True)
    cancMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancMensualidad1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancDescripcion2 = models.CharField(max_length=255, null=True, blank=True)
    cancMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancMensualidad2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancDescripcion3 = models.CharField(max_length=255, null=True, blank=True)
    cancMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancMensualidad3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancDescripcion4 = models.CharField(max_length=255, null=True, blank=True)
    cancMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancMensualidad4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancDescripcion5 = models.CharField(max_length=255, null=True, blank=True)
    cancMonto5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancMensualidad5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancRefiSaldo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #------
    
    formaPago = models.IntegerField(null=True)
    periodoPago = models.IntegerField(null=True, default=1)
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE, null=True)
    pagaDiciembre = models.CharField(
        max_length=10,
        choices=[('NO', 'NO'), ('SI', 'SI')],
        default='NO',
        null=True,
        blank=True
    )
    selectDescuento = models.CharField(
        max_length=1,
        choices=[('Y', 'Y'), ('N', 'N')],
        default='N',
        blank=True,
        null=True
    )
    porServDesc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Datos de la cotización
    fechaInicioPago = models.DateField(null=True)
    montoPrestamo = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    comiCierre = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=13)
    plazoPago = models.IntegerField(null=True)
    tasaInteres = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    r_deseada = models.DecimalField(max_digits=10, decimal_places=2, null=True)
   # Datos seguro de auto
    financiaSeguro = models.BooleanField(default=True)
    mesesFinanciaSeguro = models.IntegerField(null=True,default=2,blank=True)
    montoanualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0,blank=True)
    montoMensualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    cantPagosSeguro = models.IntegerField(null=True,default=12,blank=True)
    # DATOS DEL AUTO
    valorAuto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cashback = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, blank=True)
    abono = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, blank=True)
    abonoPorcentaje = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, blank=True)
    marca = models.CharField(max_length=255, null=True, blank=True)
    modelo = models.CharField(max_length=255, null=True, blank=True)
    yearCarro = models.IntegerField(null=True, blank=True)
    transmisionAuto = models.CharField(
        max_length=20,
        choices=[('MANUAL', 'Manual'), ('AUTOMÁTICO', 'Automático')],
        default='AUTOMÁTICO',
        null=True,
        blank=True
    )
    kilometrajeAuto = models.IntegerField(null=True, default=0, blank=True)
    nuevoAuto = models.CharField(
        max_length=10,
        choices=[('AUTO NUEVO', 'Auto Nuevo'), ('AUTO USADO', 'Auto Usado')],
        default='AUTO NUEVO',
        null=True,
        blank=True
    )
    yearsFinanciamiento = models.IntegerField(null=True, default=1, blank=True)
    #DATOS DE LA CONSULTA
    observaciones = models.TextField(null=True, blank=True)
    #DETALLES DEL DEUDOR
    tiempoServicio = models.CharField(max_length=255, null=True, blank=True)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nombreEmpresa = models.CharField(max_length=255, null=True, blank=True)
    referenciasAPC = models.CharField(max_length=255, null=True, choices=REFERENCIAS_OPCIONES, blank=True)
    cartera = models.CharField(max_length=255, null=True, choices=CARTERA_OPCIONES, blank=True)
    licencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI', blank=True)
    posicion = models.CharField(max_length=255, null=True, blank=True)
    perfilUniversitario = models.CharField(max_length=255, null=True, blank=True)
    #NIVEL DE ENDEUDAMIENTO - DEUDOR
    horasExtrasMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    horasExtrasDcto = models.BooleanField(default=False, blank=True)
    primaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    primaDcto = models.BooleanField(default=False, blank=True)
    bonosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bonosDcto = models.BooleanField(default=False, blank=True)
    otrosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    otrosDcto = models.BooleanField(default=False, blank=True)
    siacapMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    siacapDcto = models.BooleanField(default=False, blank=True)
    praaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    praaDcto = models.BooleanField(default=False, blank=True)
    dirOtros1 = models.CharField(max_length=255, null=True, blank=True)
    dirOtrosMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dirOtrosDcto1 = models.BooleanField(default=False, blank=True)
    dirOtros2 = models.CharField(max_length=255, null=True, blank=True)
    dirOtrosMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dirOtrosDcto2 = models.BooleanField(default=False, blank=True)
    dirOtros3 = models.CharField(max_length=255, null=True, blank=True)
    dirOtrosMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dirOtrosDcto3 = models.BooleanField(default=False, blank=True)
    dirOtros4 = models.CharField(max_length=255, null=True, blank=True)
    dirOtrosMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dirOtrosDcto4 = models.BooleanField(default=False, blank=True)
    pagoVoluntario1 = models.CharField(max_length=255, null=True, blank=True)
    pagoVoluntarioMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pagoVoluntarioDcto1 = models.BooleanField(default=False, blank=True)
    pagoVoluntario2 = models.CharField(max_length=255, null=True, blank=True)
    pagoVoluntarioMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pagoVoluntarioDcto2 = models.BooleanField(default=False, blank=True)
    pagoVoluntario3 = models.CharField(max_length=255, null=True, blank=True)
    pagoVoluntarioMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pagoVoluntarioDcto3 = models.BooleanField(default=False, blank=True)
    pagoVoluntario4 = models.CharField(max_length=255, null=True, blank=True)
    pagoVoluntarioMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pagoVoluntarioDcto4 = models.BooleanField(default=False, blank=True)
    pagoVoluntario5 = models.CharField(max_length=255, null=True, blank=True)
    pagoVoluntarioMonto5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pagoVoluntarioDcto5 = models.BooleanField(default=False, blank=True)
    pagoVoluntario6 = models.CharField(max_length=255, null=True, blank=True)
    pagoVoluntarioMonto6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pagoVoluntarioDcto6 = models.BooleanField(default=False, blank=True)

    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, blank=True)

    #RESULTADOS COTIZACION
    tasaEstimada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tasaBruta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    r1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    auxMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wrkMontoLetra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wrkLetraSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wrkLetraSinSeguros = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calcComiCierreFinal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calcMontoNotaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calcMontoTimbres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tablaTotalPagos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tablaTotalSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tablaTotalFeci = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tablaTotalInteres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tablaTotalMontoCapital = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    manejo_5porc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    montoManejoT = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_manejo_b = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #resultado nivel - real
    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalDescuentosLegales = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalDescuentoDirecto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalPagoVoluntario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salarioNetoActual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    porSalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #resultado nivel - completo
    totalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    totalIngresosMensualesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalDescuentosLegalesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salarioNetoActualCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    porSalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    #PRORRATEO
    mes0 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes7 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes8 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes9 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes10 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes11 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    primerMes = models.CharField(max_length=10, choices=MESES_OPCIONES, null=True, blank = True)
    tipoProrrateo = models.CharField(max_length=20, choices=TIPO_PRORRATEO_OPCIONES, default='horas_extras', blank=True)

    #CODEUDOR
    aplicaCodeudor = models.CharField(
        max_length=2,
        choices=[('no', 'No'), ('si', 'Si')],
        default='no'
    )
    codeudorNombre = models.CharField(max_length=100, null=True, blank=True)
    codeudorCedula = models.CharField(max_length=20, null=True, blank=True)
    codeudorEstabilidad = models.CharField(max_length=255, null=True, blank=True)
    codeudorIngresos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codeudorCartera = models.CharField(max_length=255, null=True, choices=CARTERA_OPCIONES, blank=True)
    codeudorPosicion = models.CharField(max_length=255, null=True, blank=True)
    codeudorLicencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI', blank=True)
    codeudorEmpresa = models.CharField(max_length=255, null=True, blank=True)
    codeudorReferenciasAPC = models.CharField(max_length=255, null=True, choices=REFERENCIAS_OPCIONES, blank=True)
    codeudorNombreEmpres1 = models.CharField(max_length=255, null=True, blank=True)
    codeudorPeriodo1 = models.CharField(max_length=255, null=True, blank=True)
    codeudorSalario1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codeudorNombreEmpres2 = models.CharField(max_length=255, null=True, blank=True)
    codeudorPeriodo2 = models.CharField(max_length=255, null=True, blank=True)
    codeudorSalario2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codeudorNombreEmpres3 = models.CharField(max_length=255, null=True, blank=True)
    codeudorPeriodo3 = models.CharField(max_length=255, null=True, blank=True)
    codeudorSalario3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #NIVEL ENDEUDAMIENTO - FAMILIAR
    cohorasExtrasMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cohorasExtrasDcto = models.BooleanField(default=False, blank=True)
    coprimaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coprimaDcto = models.BooleanField(default=False, blank=True)
    cobonosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cobonosDcto = models.BooleanField(default=False, blank=True)
    cootrosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cootrosDcto = models.BooleanField(default=False, blank=True)
    cosiacapMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cosiacapDcto = models.BooleanField(default=False, blank=True)
    copraaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copraaDcto = models.BooleanField(default=False, blank=True)
    codirOtros1 = models.CharField(max_length=255, null=True, blank=True)
    codirOtrosMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codirOtrosDcto1 = models.BooleanField(default=False, blank=True)
    codirOtros2 = models.CharField(max_length=255, null=True, blank=True)
    codirOtrosMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codirOtrosDcto2 = models.BooleanField(default=False, blank=True)
    codirOtros3 = models.CharField(max_length=255, null=True, blank=True)
    codirOtrosMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codirOtrosDcto3 = models.BooleanField(default=False, blank=True)
    codirOtros4 = models.CharField(max_length=255, null=True, blank=True)
    codirOtrosMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    codirOtrosDcto4 = models.BooleanField(default=False, blank=True)
    copagoVoluntario1 = models.CharField(max_length=255, null=True, blank=True)
    copagoVoluntarioMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copagoVoluntarioDcto1 = models.BooleanField(default=False, blank=True)
    copagoVoluntario2 = models.CharField(max_length=255, null=True, blank=True)
    copagoVoluntarioMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copagoVoluntarioDcto2 = models.BooleanField(default=False, blank=True)
    copagoVoluntario3 = models.CharField(max_length=255, null=True, blank=True)
    copagoVoluntarioMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copagoVoluntarioDcto3 = models.BooleanField(default=False, blank=True)
    copagoVoluntario4 = models.CharField(max_length=255, null=True, blank=True)
    copagoVoluntarioMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copagoVoluntarioDcto4 = models.BooleanField(default=False, blank=True)
    copagoVoluntario5 = models.CharField(max_length=255, null=True, blank=True)
    copagoVoluntarioMonto5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copagoVoluntarioDcto5 = models.BooleanField(default=False, blank=True)
    copagoVoluntario6 = models.CharField(max_length=255, null=True, blank=True)
    copagoVoluntarioMonto6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    copagoVoluntarioDcto6 = models.BooleanField(default=False, blank=True)
    cototalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, blank=True)
    #Codeudor - resultado nivel - real
    cosalarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cototalDescuentosLegales = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cototalDescuentoDirecto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cototalPagoVoluntario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cosalarioNetoActual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cosalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coporSalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #Codeudor - resultado nivel - completo
    cototalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, blank=True)
    cototalIngresosMensualesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cototalDescuentosLegalesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cosalarioNetoActualCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cosalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coporSalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    #movimientos
    
    movPrimerMes = models.CharField(max_length=10, choices=MESES_OPCIONES, null=True, blank=True)
    movOpcion = models.CharField(
        max_length=20,
        choices=[('usar_valor', 'Usar valor'), ('ingresar_manual', 'Ingresar manual')],
        default='ingresar_manual',
        blank=True
    )
    ingresosMes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    egresosMes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresosMes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    egresosMes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresosMes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    egresosMes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresosMes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    egresosMes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresosMes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    egresosMes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresosMes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    egresosMes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    averageIngresos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    
    #DATOS DEL TAPEz
    hipotecaDescuentoDir = models.CharField(
        max_length=2,
        choices=[('NO', 'No'), ('SI', 'Si')],
        null=True,
        blank=True
    )
    tieneEmbargo = models.CharField(
        max_length=2,
        choices=[('NO', 'No'), ('SI', 'Si')],
        null=True,
        blank=True
    )
    letraDepende = models.CharField(
        max_length=2,
        choices=[('NO', 'No'), ('SI', 'Si')],
        null=True,
        blank=True
    )
    letraFaje = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    deducciones1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deducciones2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deducciones3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deducciones4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deducciones5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deducciones6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    cancelaciones1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancelaciones2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancelaciones3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancelaciones4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancelaciones5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancelaciones6 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    letraHipoteca1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    letraHipoteca2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


           
    
    # SAVE FUNCTION
    NumeroCotizacion = models.IntegerField(null=True, blank=True, unique=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Cotizacion, self).save(*args, **kwargs)
        if self.NumeroCotizacion is None or self.NumeroCotizacion != self.id:
            self.NumeroCotizacion = self.id
            super(Cotizacion, self).save(update_fields=['NumeroCotizacion'])
        
        #Verifica si existe el cliente
        
        cliente, created = Cliente.objects.get_or_create(
            cedulaCliente=self.cedulaCliente,
            defaults={
            'nombreCliente': self.nombreCliente,
            'fechaNacimiento': self.fechaNacimiento,
            'edad': self.edad,
            'sexo': self.sexo,
            'jubilado': self.jubilado,
            
            }
        )
        if not created:
            # Update existing Cliente fields
            cliente.nombreCliente = self.nombreCliente
            cliente.fechaNacimiento = self.fechaNacimiento
            cliente.edad = self.edad
            cliente.sexo = self.sexo
            cliente.jubilado = self.jubilado

            
            

            # Update other fields as necessary
        cliente.save()
        
            
        super(Cotizacion, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.NumeroCotizacion} - {self.nombreCliente} - {self.cedulaCliente} - {self.tipoPrestamo} - {self.id}"
    

class CotizacionDocumento(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)
    documento = models.FileField(upload_to='documentos_cotizacion/')
    def save(self, *args, **kwargs):
        if self.documento:
            self.documento.name = f"{self.cotizacion.NumeroCotizacion}/{self.documento.name}"
        super(CotizacionDocumento, self).save(*args, **kwargs)
    tipo_documento = models.CharField(max_length=255, null=True)
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.cotizacion.NumeroCotizacion} - {self.tipo_documento}"