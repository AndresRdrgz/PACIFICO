from django.db import models

class Patrono(models.Model):
    codigo = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=255)
    agrupador = models.CharField(max_length=255,blank=True, null=True)
    selectDescuento = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='N')
    porServDesc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    montoFijo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    disketCentral = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='N', blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion} - {self.agrupador} - {self.selectDescuento} - {self.porServDesc} - {self.montoFijo} - {self.disketCentral}"

class Promocion(models.Model):
    descripcion = models.CharField(max_length=255)
    comentario = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    producto = models.CharField(
        max_length=20,
        choices=[('PREST AUTO', 'Prest. Auto'), ('PERSONAL', 'Personal')]
    )
    incentivo = models.CharField(
        max_length=20,
        choices=[('EFECTIVO', 'Efectivo'), ('LETRAS', 'Letras'), ('BONO', 'Bono'), ('FECHA PAGO', 'Fecha Pago')]
    )
    dirigido_a = models.CharField(
        max_length=20,
        choices=[('CLIENTE', 'Cliente'), ('VENDEDOR', 'Vendedor'), ('AGENCIA', 'Agencia')]
    )
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
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    no_letras = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.descripcion} ({'Activa' if self.activa else 'Inactiva'})"

class TargetPromocion(models.Model):
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name="target_promociones")
    patcat = models.IntegerField(blank=True, null=True)
    agrupador = models.CharField(max_length=255, blank=True, null=True)
    todos = models.BooleanField(default=False)

    def __str__(self):
        return f"Target for {self.promocion.descripcion} - PATCAt: {self.patcat}, AGRUPADOR: {self.agrupador}, Todos: {self.todos}"

class Agencias(models.Model):
    secuencia = models.IntegerField()
    razon_social = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.secuencia} - {self.razon_social}"