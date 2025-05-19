from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from capacitaciones_app.models import Curso, GrupoAsignacion


# 🔁 SINCRONIZACIÓN: cuando se asignan grupos a cursos
@receiver(m2m_changed, sender=Curso.grupos_asignados.through)
def sync_grupo_asignacion(sender, instance, action, pk_set, reverse, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if action == 'post_add':
            for grupo_id in pk_set:
                try:
                    grupo = GrupoAsignacion.objects.get(pk=grupo_id)
                    miembros = grupo.usuarios_asignados.all()
                    instance.usuarios_asignados.add(*miembros)
                except GrupoAsignacion.DoesNotExist:
                    continue

        elif action == 'post_remove':
            for grupo_id in pk_set:
                try:
                    grupo = GrupoAsignacion.objects.get(pk=grupo_id)
                    miembros = grupo.usuarios_asignados.all()
                    for miembro in miembros:
                        sigue_siendomiembro = any(
                            miembro in g.usuarios_asignados.all()
                            for g in instance.grupos_asignados.all()
                        )
                        if not sigue_siendomiembro:
                            instance.usuarios_asignados.remove(miembro)
                except GrupoAsignacion.DoesNotExist:
                    continue

        elif action == 'post_clear':
            for grupo in GrupoAsignacion.objects.all():
                miembros = grupo.usuarios_asignados.all()
                for miembro in miembros:
                    sigue_siendomiembro = any(
                        miembro in g.usuarios_asignados.all()
                        for g in instance.grupos_asignados.all()
                    )
                    if not sigue_siendomiembro:
                        instance.usuarios_asignados.remove(miembro)


# ✅ Cuando se guarda un grupo
@receiver(post_save, sender=GrupoAsignacion)
def sync_cursos_a_usuarios(sender, instance, **kwargs):
    for curso in instance.cursos_asignados.all():  # 🔄 campo correcto en Curso
        curso.usuarios_asignados.add(*instance.usuarios_asignados.all())


# 🔁 Cuando se modifican usuarios dentro de un grupo
@receiver(m2m_changed, sender=GrupoAsignacion.usuarios_asignados.through)
def sync_usuarios_grupo(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        for curso in instance.cursos_asignados.all():  # 🔄 campo correcto en Curso
            nuevos_usuarios = set()
            for grupo in curso.grupos_asignados.all():
                nuevos_usuarios.update(grupo.usuarios_asignados.all())
            curso.usuarios_asignados.set(nuevos_usuarios)
