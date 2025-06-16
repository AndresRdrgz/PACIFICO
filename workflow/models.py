from django.db import models

# --- CHOICES GLOBALS ---
SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
]

PROVINCIA_CHOICES = [
    ('', '—'),  # Opción vacía con raya
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
]

LETRA_CEDULA_CHOICES = [
    ('', '—'),  # Opción vacía con raya
    ('E', 'E'),
    ('N', 'N'),
    ('PE', 'PE'),
    ('AV', 'AV'),
]

PRODUCTO_CHOICES = [
    ('Auto', 'Auto'),
    ('Personal', 'Personal'),
    ('Hipotecario', 'Hipotecario'),
]

NIVEL_ACADEMICO_CHOICES = [
    ('PRIMARIA', 'PRIMARIA'),
    ('SECUNDARIA', 'SECUNDARIA'),
    ('TECNICO', 'TECNICO'),
    ('UNIVERSITARIA', 'UNIVERSITARIA'),
    ('POST GRADO', 'POST GRADO'),
    ('MAESTRIA', 'MAESTRIA'),
    ('OTROS', 'OTROS'),
]

ORIGEN_FONDOS_CHOICES = [
    ('LOCAL', 'LOCAL'),
    ('EXTRANJERO', 'EXTRANJERO'),
]

# --- MODELOS ---
class ClienteEntrevista(models.Model):
    # DATOS GENERALES
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    provincia_cedula = models.CharField(max_length=2, choices=PROVINCIA_CHOICES, blank=True, null=True)
    tipo_letra = models.CharField(max_length=5, choices=LETRA_CEDULA_CHOICES, blank=True, null=True)
    tomo_cedula = models.CharField(max_length=10)
    partida_cedula = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    jubilado = models.BooleanField(default=False)
    nivel_academico = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Valores separados por coma para selección múltiple. Ej: PRIMARIA,SECUNDARIA",
    )
    
    lugar_nacimiento = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)
    no_dependientes = models.PositiveIntegerField(default=0)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_producto = models.CharField(max_length=50, choices=PRODUCTO_CHOICES)
    oficial = models.CharField(max_length=100)
    apellido_casada = models.CharField(max_length=100, blank=True, null=True)
    peso = models.DecimalField("Peso (lb)", max_digits=5, decimal_places=2, blank=True, null=True)
    estatura = models.DecimalField("Estatura (m)", max_digits=4, decimal_places=2, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, default="Panamá")
    ESTADO_CIVIL_CHOICES = [
        ('CASADO (A)', 'CASADO (A)'),
        ('UNIDO (A)', 'UNIDO (A)'),
        ('SOLTERO (A)', 'SOLTERO (A)'),
        ('VIUDO (A)', 'VIUDO (A)'),
        ('SEPARADO (A)', 'SEPARADO (A)'),
    ]
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)

    # DIRECCIÓN RESIDENCIAL
    direccion_completa = models.TextField(blank=True, null=True)
    barrio = models.CharField(max_length=100, blank=True, null=True)
    calle = models.CharField(max_length=100, blank=True, null=True)
    casa_apto = models.CharField(max_length=100, blank=True, null=True)

    # CÓNYUGE
    conyuge_nombre = models.CharField(max_length=100, blank=True, null=True)
    conyuge_cedula = models.CharField(max_length=15, blank=True, null=True)
    conyuge_lugar_trabajo = models.CharField(max_length=100, blank=True, null=True)
    conyuge_cargo = models.CharField(max_length=100, blank=True, null=True)
    conyuge_ingreso = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    conyuge_telefono = models.CharField(max_length=20, blank=True, null=True)

    # INFORMACIÓN LABORAL
    trabajo_direccion = models.TextField(blank=True, null=True)
    trabajo_lugar = models.CharField(max_length=100, blank=True, null=True)
    trabajo_cargo = models.CharField(max_length=100, blank=True, null=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    TIPO_TRABAJO_CHOICES = [
        ('ASALARIADO', 'ASALARIADO'),
        ('INDEPENDIENTE', 'INDEPENDIENTE'),
        ('ABOGADO', 'ABOGADO'),
    ]
    tipo_trabajo = models.CharField(max_length=20, choices=TIPO_TRABAJO_CHOICES, blank=True, null=True)
    FRECUENCIA_PAGO_CHOICES = [
        ('SEMANAL', 'SEMANAL'),
        ('QUINCENAL', 'QUINCENAL'),
        ('MENSUAL', 'MENSUAL'),
    ]
    frecuencia_pago = models.CharField(max_length=20, choices=FRECUENCIA_PAGO_CHOICES, blank=True, null=True)
    tel_trabajo = models.CharField(max_length=10, blank=True, null=True)
    tel_ext = models.CharField(max_length=5, blank=True, null=True)
    origen_fondos = models.CharField(max_length=20, choices=ORIGEN_FONDOS_CHOICES, blank=True, null=True)
    fecha_inicio_trabajo = models.DateField(blank=True, null=True)

    # OTROS INGRESOS
    tipo_ingreso_1 = models.CharField(max_length=100, blank=True, null=True)
    descripcion_ingreso_1 = models.CharField(max_length=255, blank=True, null=True)
    monto_ingreso_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    tipo_ingreso_2 = models.CharField(max_length=100, blank=True, null=True)
    descripcion_ingreso_2 = models.CharField(max_length=255, blank=True, null=True)
    monto_ingreso_2 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    tipo_ingreso_3 = models.CharField(max_length=100, blank=True, null=True)
    descripcion_ingreso_3 = models.CharField(max_length=255, blank=True, null=True)
    monto_ingreso_3 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # PEP
    es_pep = models.BooleanField(default=False)
    pep_ingreso = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    pep_inicio = models.DateField(blank=True, null=True)
    pep_cargo_actual = models.CharField(max_length=100, blank=True, null=True)
    pep_fin = models.DateField(blank=True, null=True)
    pep_cargo_anterior = models.CharField(max_length=100, blank=True, null=True)
    pep_fin_anterior = models.DateField(blank=True, null=True)

    # PEP FAMILIAR
    es_familiar_pep = models.BooleanField(default=False)
    parentesco_pep = models.CharField(max_length=50, blank=True, null=True)
    nombre_pep = models.CharField(max_length=100, blank=True, null=True)
    cargo_pep = models.CharField(max_length=100, blank=True, null=True)
    institucion_pep = models.CharField(max_length=100, blank=True, null=True)
    pep_fam_inicio = models.DateField(blank=True, null=True)
    pep_fam_fin = models.DateField(blank=True, null=True)

    # DATOS BANCARIOS
    banco = models.CharField(max_length=100, blank=True, null=True)
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=20, blank=True, null=True)

    # AUTORIZACIONES
    autoriza_apc = models.BooleanField(default=False)
    acepta_datos = models.BooleanField(default=False)
    es_beneficiario_final = models.BooleanField(default=False)

    # SISTEMA
    fecha_entrevista = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

    # Puedes agregar un método para mostrar los niveles académicos como lista
    def get_nivel_academico_list(self):
        if self.nivel_academico:
            return self.nivel_academico.split(',')
        return []


class ReferenciaPersonal(models.Model):
    entrevista = models.ForeignKey(
        ClienteEntrevista,
        on_delete=models.CASCADE,
        related_name='referencias_personales'
    )
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    relacion = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class ReferenciaComercial(models.Model):
    entrevista = models.ForeignKey(
        ClienteEntrevista,
        on_delete=models.CASCADE,
        related_name='referencias_comerciales'
    )
    TIPO_CHOICES = [
        ('', '---------'),
        ('COMERCIAL', 'COMERCIAL'),
        ('CLIENTES', 'CLIENTES'),
    ]
    tipo = models.CharField(max_length=100, choices=TIPO_CHOICES, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)  # <--- Cambiado aquí
    actividad = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    saldo = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nombre


class OtroIngreso(models.Model):
    cliente = models.ForeignKey(
        ClienteEntrevista,
        related_name='otros_ingresos',
        on_delete=models.CASCADE
    )
    TIPO_INGRESO_CHOICES = [
        ('', '---------'),
        ('LOCAL', 'LOCAL'),
        ('EXTRANJERO', 'EXTRANJERO'),
    ]
    tipo_ingreso = models.CharField(
        max_length=20,
        choices=TIPO_INGRESO_CHOICES,
        default='',
        blank=True,
        null=True
    )
    fuente = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.fuente
    def __str__(self):
        return self.fuente
        return self.fuente
    def __str__(self):
        return self.fuente

