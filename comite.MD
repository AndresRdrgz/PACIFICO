# 🧠 Comité de Crédito — Integración en el Sistema de Pipelines y Etapas

Este documento describe cómo se implementa la funcionalidad del **Comité de Crédito** dentro de un flujo de solicitudes basado en pipelines y etapas.

---

## 🔁 Visión General

El Comité de Crédito es una **etapa especial dentro de un pipeline**, en la que participan varios niveles jerárquicos de revisión, como:

- Supervisor de Crédito
- Gerente de Crédito
- Gerente General

A diferencia de etapas escalonadas, **todos los niveles pueden ver, revisar y opinar sobre una solicitud al mismo tiempo**, sin necesidad de aprobación previa de niveles inferiores.

---

## 🧩 Integración en el Pipeline

### ✅ Etapa del Comité

La etapa del Comité de Crédito se define como cualquier `Etapa` dentro de un `Pipeline` que cumple las siguientes condiciones:

- Nombre sugerido: `"Comité de Crédito"`
- `es_bandeja_grupal = True` → para que todos los usuarios del comité vean las solicitudes.
- Accesible por todos los usuarios asignados a roles de comité (`NivelComite`).

---

## 🧱 Nuevos Modelos para Comité

### 1. `NivelComite`

Define los distintos niveles jerárquicos que pueden participar en el comité.

```python
class NivelComite(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(help_text="Jerarquía (menor = más bajo)")
2. UsuarioNivelComite
Relaciona usuarios con niveles de comité.

python
Copiar
Editar
class UsuarioNivelComite(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nivel = models.ForeignKey(NivelComite, on_delete=models.CASCADE)
3. ParticipacionComite
Registra la opinión de cada usuario que participa en una solicitud del comité.

python
Copiar
Editar
class ParticipacionComite(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='participaciones_comite')
    nivel = models.ForeignKey(NivelComite, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comentario = models.TextField()
    resultado = models.CharField(max_length=100, choices=[...], default='PENDIENTE')
    fecha = models.DateTimeField(auto_now_add=True)
4. SolicitudEscalamientoComite (opcional)
Permite registrar que un usuario sugiere participación de un nivel superior, aunque no es obligatorio para que ese nivel participe.

python
Copiar
Editar
class SolicitudEscalamientoComite(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    solicitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    nivel_solicitado = models.ForeignKey(NivelComite, on_delete=models.PROTECT)
    comentario = models.TextField()
    atendido = models.BooleanField(default=False)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
👥 Comportamiento Funcional
Comportamiento	Detalle
Visibilidad de solicitudes del comité	Todos los niveles ven las solicitudes en la etapa "Comité de Crédito".
Participación por niveles	Cada usuario puede dejar su comentario sin esperar a otros niveles.
Escalamiento entre niveles	Opcional, solo como sugerencia de participación.
Historial de opiniones	Se registra por solicitud, nivel, usuario, comentario y resultado.
Permisos de participación	Basados en UsuarioNivelComite.

📋 Bandeja del Comité
La bandeja de trabajo del comité se genera listando todas las solicitudes cuya etapa actual es "Comité de Crédito" y donde el usuario está asignado a algún nivel:

python
Copiar
Editar
def obtener_solicitudes_comite(user):
    if UsuarioNivelComite.objects.filter(usuario=user).exists():
        return Solicitud.objects.filter(etapa_actual__nombre="Comité de Crédito")
    return Solicitud.objects.none()
📌 Consideraciones Finales
No hay orden forzoso de participación (cualquier nivel puede participar primero).

Se pueden tomar decisiones a cualquier nivel si el flujo de trabajo lo permite.

Todas las opiniones quedan registradas y trazables.

Este esquema es totalmente compatible con el sistema de Pipelines, Etapas y Subestados existente.