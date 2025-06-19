from django.db import models
from django.utils import timezone

class EncuestaSatisfaccion(models.Model):
    DEPARTAMENTO_CHOICES = [
        ("CONTABILIDAD", "CONTABILIDAD"),
        ("COBROS", "COBROS"),
        ("CÓMPUTO", "CÓMPUTO"),
        ("EXPERIENCIA AL CLIENTE", "EXPERIENCIA AL CLIENTE"),
        ("FINANZAS", "FINANZAS"),
        ("GERENCIA", "GERENCIA"),
        ("ITICO", "ITICO"),
        ("LEGAL", "LEGAL"),
        ("NEGOCIOS", "NEGOCIOS"),
        ("PROCESOS", "PROCESOS"),
        ("RECURSOS HUMANOS- ADM", "RECURSOS HUMANOS- ADM"),
        ("SERVICIOS GENERALES", "SERVICIOS GENERALES"),
        ("TRAMITE", "TRAMITE"),
    ]
    CARGO_CHOICES = [
        ("Asistente", "Asistente"),
        ("Analista", "Analista"),
        ("Oficial/Profesional", "Oficial/Profesional"),
        ("Coordinador", "Coordinador"),
        ("Encargada/Supervisor", "Encargada/Supervisor"),
        ("Jefe", "Jefe"),
        ("Gerente", "Gerente"),
    ]
    departamento = models.CharField(max_length=40, choices=DEPARTAMENTO_CHOICES)
    cargo = models.CharField(max_length=30, choices=CARGO_CHOICES)
    expositor = models.PositiveSmallIntegerField()
    utilidad = models.CharField(max_length=2)
    satisfaccion = models.PositiveSmallIntegerField()
    aprendido = models.TextField(max_length=300)
    lugar = models.CharField(max_length=20)
    rol = models.CharField(max_length=20)
    recomendacion = models.TextField(max_length=200, blank=True)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.departamento} - {self.cargo} ({self.fecha:%Y-%m-%d})"
