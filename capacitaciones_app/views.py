from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Curso, Modulo, Tema, ProgresoCurso, ProgresoTema, ArchivoAdicional

# 🧾 Vista: Lista de cursos
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'capacitaciones_app/cursos.html', {'cursos': cursos})


# 📘 Vista: Detalle de curso con progreso y módulos
@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    progreso = ProgresoCurso.objects.filter(usuario=request.user, curso=curso).first()

    total_modulos = curso.modulos.count()
    completados = progreso.modulos_completados.count() if progreso else 0

    progreso_percent = round((completados / total_modulos) * 100) if total_modulos > 0 else 0

    temas_completados_ids = ProgresoTema.objects.filter(
        usuario=request.user, completado=True
    ).values_list('tema_id', flat=True)

    def get_color_from_text(texto):
        letra = texto[0].lower()
        if letra in "abc":
            return "#007bff"
        elif letra in "def":
            return "#28a745"
        elif letra in "ghi":
            return "#17a2b8"
        elif letra in "jkl":
            return "#ffc107"
        elif letra in "mno":
            return "#dc3545"
        elif letra in "pqr":
            return "#20c997"
        else:
            return "#6c757d"

    color_portada = get_color_from_text(curso.titulo)

    return render(request, 'capacitaciones_app/detalle_curso.html', {
        'curso': curso,
        'progreso': progreso,
        'total_modulos': total_modulos,
        'completados': completados,
        'progreso_percent': progreso_percent,
        'color_portada': color_portada,
        'temas_completados_ids': temas_completados_ids,
    })


# 📂 Vista: Ver tema individual (incluye archivos adicionales)
@login_required
def ver_tema(request, curso_id, tema_id):
    curso = get_object_or_404(Curso, id=curso_id)
    tema = get_object_or_404(Tema, id=tema_id)

    completado = ProgresoTema.objects.filter(usuario=request.user, tema=tema, completado=True).exists()
    archivos = tema.archivos.all()

    return render(request, 'capacitaciones_app/ver_tema.html', {
        'curso': curso,
        'tema': tema,
        'completado': completado,
        'archivos': archivos,
    })


# ✅ Marcar tema como completado
@login_required
def marcar_tema_completado(request, tema_id):
    tema = get_object_or_404(Tema, id=tema_id)

    progreso, creado = ProgresoTema.objects.get_or_create(
        usuario=request.user,
        tema=tema
    )

    progreso.completado = True
    progreso.fecha_completado = timezone.now()
    progreso.save()

    # ⚙️ Lógica de progreso por módulo
    total_temas = tema.modulo.temas.count()
    temas_completados = ProgresoTema.objects.filter(
        usuario=request.user,
        tema__modulo=tema.modulo,
        completado=True
    ).count()

    if total_temas > 0 and temas_completados == total_temas:
        progreso_curso, _ = ProgresoCurso.objects.get_or_create(usuario=request.user, curso=tema.modulo.curso)
        progreso_curso.modulos_completados.add(tema.modulo)

        # ⚙️ Lógica de curso completo
        total_modulos = tema.modulo.curso.modulos.count()
        if progreso_curso.modulos_completados.count() == total_modulos:
            progreso_curso.completado = True
            progreso_curso.fecha_completado = timezone.now()

        progreso_curso.save()

    return redirect('ver_tema', curso_id=tema.modulo.curso.id, tema_id=tema.id)
