from django.db import models
from django.contrib.auth.models import User

class EncuestaSatisfaccionCurso(models.Model):
    DEPARTAMENTOS = [
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
    CARGOS = [
        ("Asistente", "Asistente"),
        ("Analista", "Analista"),
        ("Oficial/Profesional", "Oficial/Profesional"),
        ("Coordinador", "Coordinador"),
        ("Encargada/Supervisor", "Encargada/Supervisor"),
        ("Jefe", "Jefe"),
        ("Gerente", "Gerente"),
    ]
    LUGARES = [
        ("Presencial", "Presencial"),
        ("Virtual", "Virtual"),
        ("Mixto", "Mixto"),
    ]
    ROLES = [
        ("Participante", "Participante"),
        ("Expositor", "Expositor"),
        ("Organizador", "Organizador"),
        ("Otro", "Otro"),
    ]

    departamento = models.CharField(max_length=40, choices=DEPARTAMENTOS)
    cargo = models.CharField(max_length=30, choices=CARGOS)
    expositor = models.PositiveSmallIntegerField()  # 1-5
    utilidad = models.CharField(max_length=2, choices=[('si', 'Sí'), ('no', 'No')])
    satisfaccion = models.PositiveSmallIntegerField()  # 1-5
    aprendido = models.TextField(max_length=300)
    lugar = models.CharField(max_length=15, choices=LUGARES)
    rol = models.CharField(max_length=20, choices=ROLES)
    recomendacion = models.TextField(max_length=200, blank=True)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encuesta {self.departamento} - {self.cargo} - {self.fecha:%Y-%m-%d}"