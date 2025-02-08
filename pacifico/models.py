from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    tipoDocumento = models.CharField(max_length=10, choices=[('CEDULA', 'Cédula'), ('PASAPORTE', 'Pasaporte')], default='CEDULA')
    nombreCliente = models.CharField(max_length=255, null=True)
    fechaNacimiento = models.DateField(null=True)
    edad = models.IntegerField(null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
    jubilado = models.CharField(max_length=10, choices=JUBILADO_CHOICES, default='NO')
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE, null=True)
    patrono = models.CharField(max_length=255, null=True)
    apcScore = models.IntegerField(null=True)
    apcPI = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    #Detalles del cliente
    tiempoServicio = models.CharField(max_length=255, null=True)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    referenciasAPC = models.CharField(max_length=255, null=True, choices=REFERENCIAS_OPCIONES)
    cartera = models.CharField(max_length=255, null=True, choices=CARTERA_OPCIONES)
    licencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI')
    posicion = models.CharField(max_length=255, null=True)
    perfilUniversitario = models.CharField(max_length=255, null=True)
    #Nivel endeudamiento
    horasExtrasMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    horasExtrasDcto = models.BooleanField(default=False)
    primaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    primaDcto = models.BooleanField(default=False)
    bonosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bonosDcto = models.BooleanField(default=False)
    otrosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    otrosDcto = models.BooleanField(default=False)
    siacapMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    siacapDcto = models.BooleanField(default=False)
    praaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    praaDcto = models.BooleanField(default=False)
    dirOtros1 = models.CharField(max_length=255, null=True)
    dirOtrosMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto1 = models.BooleanField(default=False)
    dirOtros2 = models.CharField(max_length=255, null=True)
    dirOtrosMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto2 = models.BooleanField(default=False)
    dirOtros3 = models.CharField(max_length=255, null=True)
    dirOtrosMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto3 = models.BooleanField(default=False)
    dirOtros4 = models.CharField(max_length=255, null=True)
    dirOtrosMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto4 = models.BooleanField(default=False)
    pagoVoluntario1 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto1 = models.BooleanField(default=False)
    pagoVoluntario2 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto2 = models.BooleanField(default=False)
    pagoVoluntario3 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto3 = models.BooleanField(default=False)
    pagoVoluntario4 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto4 = models.BooleanField(default=False)
    pagoVoluntario5 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto5 = models.BooleanField(default=False)
    pagoVoluntario6 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto6 = models.BooleanField(default=False)

    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalDescuentosLegales = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalDescuentoDirecto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalPagoVoluntario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNetoActual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porSalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
     #resultado nivel - completo
    totalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    totalIngresosMensualesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    totalDescuentosLegalesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNetoActualCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porSalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
     #PRORRATEO
    mes0 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes7 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes8 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes9 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes10 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes11 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    primerMes = models.CharField(max_length=10, choices=MESES_OPCIONES, null=True)
    tipoProrrateo = models.CharField(max_length=20, choices=TIPO_PRORRATEO_OPCIONES, default='horas_extras')

    #MOVIMIENTOS BANCARIOS
    movPrimerMes = models.CharField(max_length=10, choices=MESES_OPCIONES, null=True)
    
    
       


    

    
    def __str__(self):
        return f"{self.nombreCliente} - {self.cedulaCliente}"
    


class Cotizacion(models.Model):
    
   
   
    #OFICIAL
    oficial = models.CharField(max_length=255, choices=OFICIAL_OPCIONES,null=True)
    sucursal = models.CharField(max_length=255, choices=SUCURSALES_OPCIONES,null=True)

    #Datos del cliente
    nombreCliente = models.CharField(max_length=100, null=True)
    cedulaCliente = models.CharField(max_length=10, null=True,default='')
    tipoDocumento = models.CharField(max_length=10, choices=[('CEDULA', 'Cédula'), ('PASAPORTE', 'Pasaporte')], default='CEDULA')
    fechaNacimiento = models.DateField(null=True)
    edad = models.IntegerField(null=True)
    sexo= models.CharField(max_length=10, choices=SEXO_OPCIONES, default='MASCULINO')
    jubilado = models.CharField(max_length=10, choices=JUBILADO_CHOICES, default='NO')
    apcScore = models.IntegerField(null=True)
    apcPI = models.DecimalField(max_digits=10, decimal_places=2, null=True)
   
    #Parametros de la Cotizacion
    patrono = models.CharField(max_length=255, null=True)
    patronoCodigo = models.IntegerField(null=True)
    vendedor = models.CharField(max_length=255, null=True)
    vendedorComision = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    formaPago = models.IntegerField(null=True)
    periodoPago = models.IntegerField(null=True, default=1)
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE, null=True)
    # Datos de la cotización
    fechaInicioPago = models.DateField(null=True)
    montoPrestamo = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    comiCierre = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=13)
    plazoPago = models.IntegerField(null=True)
    tasaInteres = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    r_deseada = models.DecimalField(max_digits=10, decimal_places=2, null=True)
   # Datos seguro de auto
    financiaSeguro = models.BooleanField(default=True)
    mesesFinanciaSeguro = models.IntegerField(null=True,default=3)
    montoanualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    montoMensualSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    cantPagosSeguro = models.IntegerField(null=True,default=12)
    # DATOS DEL AUTO
    valorAuto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cashback = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    abono = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    abonoPorcentaje = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    marca = models.CharField(max_length=255, null=True)
    modelo = models.CharField(max_length=255, null=True)
    yearCarro = models.IntegerField(null=True)
    transmisionAuto = models.CharField(
        max_length=20,
        choices=[('MANUAL', 'Manual'), ('AUTOMÁTICO', 'Automático')],
        default='AUTOMÁTICO',
        null=True
    )
    kilometrajeAuto = models.IntegerField(null=True, default=0)
    nuevoAuto = models.CharField(
        max_length=10,
        choices=[('AUTO NUEVO', 'Auto Nuevo'), ('AUTO USADO', 'Auto Usado')],
        default='AUTO NUEVO',
        null=True
    )
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
    horasExtrasMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    horasExtrasDcto = models.BooleanField(default=False)
    primaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    primaDcto = models.BooleanField(default=False)
    bonosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bonosDcto = models.BooleanField(default=False)
    otrosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    otrosDcto = models.BooleanField(default=False)
    siacapMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    siacapDcto = models.BooleanField(default=False)
    praaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    praaDcto = models.BooleanField(default=False)
    dirOtros1 = models.CharField(max_length=255, null=True)
    dirOtrosMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto1 = models.BooleanField(default=False)
    dirOtros2 = models.CharField(max_length=255, null=True)
    dirOtrosMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto2 = models.BooleanField(default=False)
    dirOtros3 = models.CharField(max_length=255, null=True)
    dirOtrosMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto3 = models.BooleanField(default=False)
    dirOtros4 = models.CharField(max_length=255, null=True)
    dirOtrosMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    dirOtrosDcto4 = models.BooleanField(default=False)
    pagoVoluntario1 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto1 = models.BooleanField(default=False)
    pagoVoluntario2 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto2 = models.BooleanField(default=False)
    pagoVoluntario3 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto3 = models.BooleanField(default=False)
    pagoVoluntario4 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto4 = models.BooleanField(default=False)
    pagoVoluntario5 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto5 = models.BooleanField(default=False)
    pagoVoluntario6 = models.CharField(max_length=255, null=True)
    pagoVoluntarioMonto6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    pagoVoluntarioDcto6 = models.BooleanField(default=False)

    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)

    #RESULTADOS COTIZACION
    tasaEstimada = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tasaBruta = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    r1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    auxMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    wrkMontoLetra = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    wrkLetraSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    wrkLetraSinSeguros = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    calcComiCierreFinal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    calcMontoNotaria = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    calcMontoTimbres = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalPagos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalSeguro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalFeci = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalInteres = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tablaTotalMontoCapital = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    manejo_5porc = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    montoManejoT = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    monto_manejo_b = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    #resultado nivel - real
    salarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalDescuentosLegales = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalDescuentoDirecto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalPagoVoluntario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNetoActual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porSalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    #resultado nivel - completo
    totalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    totalIngresosMensualesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    totalDescuentosLegalesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNetoActualCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porSalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    #PRORRATEO
    mes0 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes7 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes8 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes9 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes10 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mes11 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    primerMes = models.CharField(max_length=10, choices=MESES_OPCIONES, null=True)
    tipoProrrateo = models.CharField(max_length=20, choices=TIPO_PRORRATEO_OPCIONES, default='horas_extras')

    #CODEUDOR
    aplicaCodeudor = models.CharField(
        max_length=2,
        choices=[('no', 'No'), ('si', 'Si')],
        default='no'
    )
    codeudorNombre = models.CharField(max_length=100, null=True)
    codeudorCedula = models.CharField(max_length=20, null=True)
    codeudorEstabilidad = models.CharField(max_length=255, null=True)
    codeudorIngresos = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codeudorCartera = models.CharField(max_length=255, null=True, choices=CARTERA_OPCIONES)
    codeudorPosicion = models.CharField(max_length=255, null=True)
    codeudorLicencia = models.CharField(max_length=10, choices=LICENCIA_OPCIONES, default='SI')
    codeudorEmpresa = models.CharField(max_length=255, null=True)
    codeudorReferenciasAPC = models.CharField(max_length=255, null=True, choices=REFERENCIAS_OPCIONES)
    codeudorNombreEmpres1 = models.CharField(max_length=255, null=True)
    codeudorPeriodo1 = models.CharField(max_length=255, null=True)
    codeudorSalario1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codeudorNombreEmpres2 = models.CharField(max_length=255, null=True)
    codeudorPeriodo2 = models.CharField(max_length=255, null=True)
    codeudorSalario2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codeudorNombreEmpres3 = models.CharField(max_length=255, null=True)
    codeudorPeriodo3 = models.CharField(max_length=255, null=True)
    codeudorSalario3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    #NIVEL ENDEUDAMIENTO - FAMILIAR
    cohorasExtrasMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cohorasExtrasDcto = models.BooleanField(default=False)
    coprimaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    coprimaDcto = models.BooleanField(default=False)
    cobonosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cobonosDcto = models.BooleanField(default=False)
    cootrosMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cootrosDcto = models.BooleanField(default=False)
    cosiacapMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cosiacapDcto = models.BooleanField(default=False)
    copraaMonto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copraaDcto = models.BooleanField(default=False)
    codirOtros1 = models.CharField(max_length=255, null=True)
    codirOtrosMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codirOtrosDcto1 = models.BooleanField(default=False)
    codirOtros2 = models.CharField(max_length=255, null=True)
    codirOtrosMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codirOtrosDcto2 = models.BooleanField(default=False)
    codirOtros3 = models.CharField(max_length=255, null=True)
    codirOtrosMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codirOtrosDcto3 = models.BooleanField(default=False)
    codirOtros4 = models.CharField(max_length=255, null=True)
    codirOtrosMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    codirOtrosDcto4 = models.BooleanField(default=False)
    copagoVoluntario1 = models.CharField(max_length=255, null=True)
    copagoVoluntarioMonto1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copagoVoluntarioDcto1 = models.BooleanField(default=False)
    copagoVoluntario2 = models.CharField(max_length=255, null=True)
    copagoVoluntarioMonto2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copagoVoluntarioDcto2 = models.BooleanField(default=False)
    copagoVoluntario3 = models.CharField(max_length=255, null=True)
    copagoVoluntarioMonto3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copagoVoluntarioDcto3 = models.BooleanField(default=False)
    copagoVoluntario4 = models.CharField(max_length=255, null=True)
    copagoVoluntarioMonto4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copagoVoluntarioDcto4 = models.BooleanField(default=False)
    copagoVoluntario5 = models.CharField(max_length=255, null=True)
    copagoVoluntarioMonto5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copagoVoluntarioDcto5 = models.BooleanField(default=False)
    copagoVoluntario6 = models.CharField(max_length=255, null=True)
    copagoVoluntarioMonto6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    copagoVoluntarioDcto6 = models.BooleanField(default=False)
    cototalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    #Codeudor - resultado nivel - real
    cosalarioBaseMensual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cototalDescuentosLegales = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cototalDescuentoDirecto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cototalPagoVoluntario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cosalarioNetoActual = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cosalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    coporSalarioNeto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    #Codeudor - resultado nivel - completo
    cototalIngresosAdicionales = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    cototalIngresosMensualesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cototalDescuentosLegalesCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cosalarioNetoActualCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cosalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    coporSalarioNetoCompleto = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    #movimientos
    
    movPrimerMes = models.CharField(max_length=10, choices=MESES_OPCIONES, null=True)
    movOpcion = models.CharField(
        max_length=20,
        choices=[('usar_valor', 'Usar valor'), ('ingresar_manual', 'Ingresar manual')],
        default='ingresar_manual'
    )
    ingresosMes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    egresosMes1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ingresosMes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    egresosMes2 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ingresosMes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    egresosMes3 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ingresosMes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    egresosMes4 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ingresosMes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    egresosMes5 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ingresosMes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    egresosMes6 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    averageIngresos = models.DecimalField(max_digits=10, decimal_places=2, null=True)

 

           
    
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
        
        #Verifica si existe el cliente
        
        cliente, created = Cliente.objects.get_or_create(
            cedulaCliente=self.cedulaCliente,
            defaults={
            'nombreCliente': self.nombreCliente,
            'fechaNacimiento': self.fechaNacimiento,
            'edad': self.edad,
            'sexo': self.sexo,
            'jubilado': self.jubilado,
            'patrono': self.patrono,
            'apcScore': self.apcScore,
            'apcPI': self.apcPI,
            'aseguradora': self.aseguradora,
            'tiempoServicio': self.tiempoServicio,
            'ingresos': self.ingresos,
            'referenciasAPC': self.referenciasAPC,
            'cartera': self.cartera,
            'licencia': self.licencia,
            'posicion': self.posicion,
            'perfilUniversitario': self.perfilUniversitario,
            'siacapMonto': self.siacapMonto,
            'siacapDcto': self.siacapDcto,
            'praaMonto': self.praaMonto,
            'praaDcto': self.praaDcto,
            'dirOtros1': self.dirOtros1,
            'dirOtrosMonto1': self.dirOtrosMonto1,
            'dirOtrosDcto1': self.dirOtrosDcto1,
            'dirOtros2': self.dirOtros2,
            'dirOtrosMonto2': self.dirOtrosMonto2,
            'dirOtrosDcto2': self.dirOtrosDcto2,
            'dirOtros3': self.dirOtros3,
            'dirOtrosMonto3': self.dirOtrosMonto3,
            'dirOtrosDcto3': self.dirOtrosDcto3,
            'dirOtros4': self.dirOtros4,
            'dirOtrosMonto4': self.dirOtrosMonto4,
            'dirOtrosDcto4': self.dirOtrosDcto4,
            'pagoVoluntario1': self.pagoVoluntario1,
            'pagoVoluntarioMonto1': self.pagoVoluntarioMonto1,
            'pagoVoluntarioDcto1': self.pagoVoluntarioDcto1,
            'pagoVoluntario2': self.pagoVoluntario2,
            'pagoVoluntarioMonto2': self.pagoVoluntarioMonto2,
            'pagoVoluntarioDcto2': self.pagoVoluntarioDcto2,
            'pagoVoluntario3': self.pagoVoluntario3,
            'pagoVoluntarioMonto3': self.pagoVoluntarioMonto3,
            'pagoVoluntarioDcto3': self.pagoVoluntarioDcto3,
            'pagoVoluntario4': self.pagoVoluntario4,
            'pagoVoluntarioMonto4': self.pagoVoluntarioMonto4,
            'pagoVoluntarioDcto4': self.pagoVoluntarioDcto4,
            'pagoVoluntario5': self.pagoVoluntario5,
            'pagoVoluntarioMonto5': self.pagoVoluntarioMonto5,
            'pagoVoluntarioDcto5': self.pagoVoluntarioDcto5,
            'pagoVoluntario6': self.pagoVoluntario6,
            'pagoVoluntarioMonto6': self.pagoVoluntarioMonto6,
            'pagoVoluntarioDcto6': self.pagoVoluntarioDcto6,
            'salarioBaseMensual': self.salarioBaseMensual,
            'totalDescuentosLegales': self.totalDescuentosLegales,
            'totalDescuentoDirecto': self.totalDescuentoDirecto,
            'totalPagoVoluntario': self.totalPagoVoluntario,
            'salarioNetoActual': self.salarioNetoActual,
            'salarioNeto': self.salarioNeto,
            'porSalarioNeto': self.porSalarioNeto,
            'totalIngresosAdicionales': self.totalIngresosAdicionales,
            'totalIngresosMensualesCompleto': self.totalIngresosMensualesCompleto,
            'totalDescuentosLegalesCompleto': self.totalDescuentosLegales,
            'salarioNetoActualCompleto': self.salarioNetoActual,
            'salarioNetoCompleto': self.salarioNeto,
            'porSalarioNetoCompleto': self.porSalarioNeto,
            'horasExtrasMonto': self.horasExtrasMonto,
            'horasExtrasDcto': self.horasExtrasDcto,
            'primaMonto': self.primaMonto,
            'primaDcto': self.primaDcto,
            'bonosMonto': self.bonosMonto,
            'bonosDcto': self.bonosDcto,
            'otrosMonto': self.otrosMonto,
            'otrosDcto': self.otrosDcto,
            'mes0': self.mes0,
            'mes1': self.mes1,
            'mes2': self.mes2,
            'mes3': self.mes3,
            'mes4': self.mes4,
            'mes5': self.mes5,
            'mes6': self.mes6,
            'mes7': self.mes7,
            'mes8': self.mes8,
            'mes9': self.mes9,
            'mes10': self.mes10,
            'mes11': self.mes11,
            'primerMes': self.primerMes,
            'tipoProrrateo': self.tipoProrrateo,
            'tipoDocumento': self.tipoDocumento,


            }
        )
        if not created:
            # Update existing Cliente fields
            cliente.nombreCliente = self.nombreCliente
            cliente.fechaNacimiento = self.fechaNacimiento
            cliente.edad = self.edad
            cliente.sexo = self.sexo
            cliente.jubilado = self.jubilado
            cliente.patrono = self.patrono
            cliente.apcScore = self.apcScore
            cliente.apcPI = self.apcPI
            cliente.aseguradora = self.aseguradora
            cliente.tiempoServicio = self.tiempoServicio
            cliente.ingresos = self.ingresos
            cliente.referenciasAPC = self.referenciasAPC
            cliente.cartera = self.cartera
            cliente.licencia = self.licencia
            cliente.posicion = self.posicion
            cliente.perfilUniversitario = self.perfilUniversitario
            cliente.siacapMonto = self.siacapMonto
            cliente.siacapDcto = self.siacapDcto
            cliente.praaMonto = self.praaMonto
            cliente.praaDcto = self.praaDcto
            cliente.dirOtros1 = self.dirOtros1
            cliente.dirOtrosMonto1 = self.dirOtrosMonto1
            cliente.dirOtrosDcto1 = self.dirOtrosDcto1
            cliente.dirOtros2 = self.dirOtros2
            cliente.dirOtrosMonto2 = self.dirOtrosMonto2
            cliente.dirOtrosDcto2 = self.dirOtrosDcto2
            cliente.dirOtros3 = self.dirOtros3
            cliente.dirOtrosMonto3 = self.dirOtrosMonto3    
            cliente.dirOtrosDcto3 = self.dirOtrosDcto3
            cliente.dirOtros4 = self.dirOtros4
            cliente.dirOtrosMonto4 = self.dirOtrosMonto4
            cliente.dirOtrosDcto4 = self.dirOtrosDcto4
            cliente.pagoVoluntario1 = self.pagoVoluntario1
            cliente.pagoVoluntarioMonto1 = self.pagoVoluntarioMonto1
            cliente.pagoVoluntarioDcto1 = self.pagoVoluntarioDcto1
            cliente.pagoVoluntario2 = self.pagoVoluntario2
            cliente.pagoVoluntarioMonto2 = self.pagoVoluntarioMonto2
            cliente.pagoVoluntarioDcto2 = self.pagoVoluntarioDcto2
            cliente.pagoVoluntario3 = self.pagoVoluntario3
            cliente.pagoVoluntarioMonto3 = self.pagoVoluntarioMonto3
            cliente.pagoVoluntarioDcto3 = self.pagoVoluntarioDcto3
            cliente.pagoVoluntario4 = self.pagoVoluntario4
            cliente.pagoVoluntarioMonto4 = self.pagoVoluntarioMonto4
            cliente.pagoVoluntarioDcto4 = self.pagoVoluntarioDcto4
            cliente.salarioBaseMensual = self.salarioBaseMensual
            cliente.totalDescuentosLegales = self.totalDescuentosLegales
            cliente.totalDescuentoDirecto = self.totalDescuentoDirecto
            cliente.totalPagoVoluntario = self.totalPagoVoluntario
            cliente.salarioNetoActual = self.salarioNetoActual
            cliente.salarioNeto = self.salarioNeto
            cliente.porSalarioNeto = self.porSalarioNeto
            cliente.totalIngresosAdicionales = self.totalIngresosAdicionales
            cliente.totalIngresosMensualesCompleto = self.totalIngresosMensualesCompleto
            cliente.totalDescuentosLegalesCompleto = self.totalDescuentosLegales
            cliente.salarioNetoActualCompleto = self.salarioNetoActual
            cliente.salarioNetoCompleto = self.salarioNeto
            cliente.porSalarioNetoCompleto = self.porSalarioNeto
            cliente.horasExtrasMonto = self.horasExtrasMonto
            cliente.horasExtrasDcto = self.horasExtrasDcto
            cliente.primaMonto = self.primaMonto
            cliente.primaDcto = self.primaDcto
            cliente.bonosMonto = self.bonosMonto
            cliente.bonosDcto = self.bonosDcto
            cliente.otrosMonto = self.otrosMonto
            cliente.otrosDcto = self.otrosDcto
            cliente.mes0 = self.mes0
            cliente.mes1 = self.mes1
            cliente.mes2 = self.mes2
            cliente.mes3 = self.mes3
            cliente.mes4 = self.mes4
            cliente.mes5 = self.mes5
            cliente.mes6 = self.mes6
            cliente.mes7 = self.mes7
            cliente.mes8 = self.mes8
            cliente.mes9 = self.mes9
            cliente.mes10 = self.mes10
            cliente.mes11 = self.mes11
            cliente.primerMes = self.primerMes
            cliente.tipoProrrateo = self.tipoProrrateo
            cliente.tipoDocumento = self.tipoDocumento
          

            # Update other fields as necessary
        cliente.save()
        
            
        super(Cotizacion, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.NumeroCotizacion} - {self.nombreCliente} - {self.cedulaCliente}"
    

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