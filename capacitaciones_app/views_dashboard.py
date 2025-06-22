from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from .models import (
    Curso, Asignacion, ProgresoCurso, GrupoAsignacion,
    Modulo, Tema, Quiz, Pregunta, ResultadoQuiz, Feedback
)


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_view(request):
    """Vista principal del dashboard - Todos los cálculos en la vista"""
    
    # Obtener conteos básicos
    total_cursos = Curso.objects.count()
    total_usuarios = User.objects.filter(is_active=True).count()
    total_asignaciones = Asignacion.objects.count()
    total_cursos_completados = ProgresoCurso.objects.filter(completado=True).count()
    
    # KPIs adicionales
    total_modulos = Modulo.objects.count()
    total_temas = Tema.objects.count()
    total_quizzes = Quiz.objects.count()
    total_preguntas = Pregunta.objects.count()
    total_grupos = GrupoAsignacion.objects.count()
    total_resultados_quiz = ResultadoQuiz.objects.count()
    total_feedbacks = Feedback.objects.count()
    
    # NUEVAS MÉTRICAS DE DURACIÓN
    from django.db.models import Sum, Avg
    cursos_con_duracion = Curso.objects.filter(duracion_horas__isnull=False)
    total_horas_disponibles = cursos_con_duracion.aggregate(Sum('duracion_horas'))['duracion_horas__sum'] or 0
    promedio_duracion_curso = cursos_con_duracion.aggregate(Avg('duracion_horas'))['duracion_horas__avg'] or 0
    total_cursos_con_duracion = cursos_con_duracion.count()
    
    # Horas de capacitación completadas (aproximado)
    total_horas_completadas = 0
    if total_cursos_completados > 0 and promedio_duracion_curso > 0:
        # Usar el promedio de duración para estimar horas completadas
        total_horas_completadas = round(total_cursos_completados * float(promedio_duracion_curso), 1)
    
    # Métricas de progreso
    total_asignaciones_activas = Asignacion.objects.filter(fecha__isnull=False).count()
    total_usuarios_con_asignaciones = User.objects.filter(asignacion__isnull=False).distinct().count()
    total_cursos_con_modulos = Curso.objects.filter(modulos__isnull=False).distinct().count()
    
    # CÁLCULOS DE PORCENTAJES
    # Tasa de finalización
    tasa_completado = 0
    if total_asignaciones > 0:
        tasa_completado = round((total_cursos_completados / total_asignaciones) * 100)
    
    # Tasa de participación
    tasa_participacion = 0
    if total_usuarios > 0:
        tasa_participacion = round((total_usuarios_con_asignaciones / total_usuarios) * 100)
    
    # Tasa de finalización para KPIs
    tasa_finalizacion = 0
    if total_asignaciones > 0:
        tasa_finalizacion = round((total_cursos_completados / total_asignaciones) * 100)
    
    # Participación activa para KPIs
    participacion_activa = 0
    if total_usuarios > 0:
        participacion_activa = round((total_usuarios_con_asignaciones / total_usuarios) * 100)
    
    # Cursos con evaluación
    cursos_con_quiz = 0
    if total_cursos > 0:
        cursos_con_quiz = round((total_quizzes / total_cursos) * 100)
    
    # Nivel de feedback
    nivel_feedback = 0
    if total_asignaciones > 0:
        nivel_feedback = round((total_feedbacks / total_asignaciones) * 100)
    
    # CÁLCULOS DE PROMEDIOS
    # Módulos promedio por curso
    promedio_modulos = 0
    if total_cursos > 0:
        promedio_modulos = round(total_modulos / total_cursos, 1)
    
    # Temas promedio por módulo
    promedio_temas = 0
    if total_modulos > 0:
        promedio_temas = round(total_temas / total_modulos, 1)
    
    # Preguntas promedio por quiz
    promedio_preguntas = 0
    if total_quizzes > 0:
        promedio_preguntas = round(total_preguntas / total_quizzes, 1)
    
    # Asignaciones promedio por usuario
    promedio_asignaciones = 0
    if total_usuarios_con_asignaciones > 0:
        promedio_asignaciones = round(total_asignaciones / total_usuarios_con_asignaciones, 1)
    
    # ESTADO DEL SISTEMA
    sistema_activo = total_asignaciones > 0
    
    # ALERTAS Y RECOMENDACIONES
    alertas = []
    if total_cursos == 0:
        alertas.append({"tipo": "warning", "mensaje": "Sin cursos disponibles - Crear contenido educativo"})
    elif total_modulos == 0:
        alertas.append({"tipo": "info", "mensaje": "Agregar módulos para estructurar los cursos"})
    
    if total_usuarios_con_asignaciones == 0:
        alertas.append({"tipo": "warning", "mensaje": "Sin usuarios asignados - Crear asignaciones"})
    
    if total_quizzes == 0:
        alertas.append({"tipo": "info", "mensaje": "Agregar quizzes para evaluar el aprendizaje"})
    
    if total_feedbacks == 0:
        alertas.append({"tipo": "info", "mensaje": "Fomentar feedback para mejorar los cursos"})
    
    if total_asignaciones > 0 and total_cursos_completados == 0:
        alertas.append({"tipo": "warning", "mensaje": "Ningún curso completado - Seguimiento necesario"})
    
    if total_grupos == 0:
        alertas.append({"tipo": "info", "mensaje": "Crear grupos para facilitar la gestión"})
    
    if (total_cursos > 0 and total_modulos > 0 and 
        total_asignaciones > 0 and total_cursos_completados > 0):
        alertas.append({"tipo": "success", "mensaje": "Sistema funcionando correctamente"})

    return render(request, 'capacitaciones_app/dashboard_modern.html', {
        # Conteos básicos
        'total_cursos': total_cursos,
        'total_usuarios': total_usuarios,
        'total_asignaciones': total_asignaciones,
        'total_cursos_completados': total_cursos_completados,
        'total_modulos': total_modulos,
        'total_temas': total_temas,
        'total_quizzes': total_quizzes,
        'total_preguntas': total_preguntas,
        'total_grupos': total_grupos,
        'total_feedbacks': total_feedbacks,
        'total_resultados_quiz': total_resultados_quiz,
        'total_usuarios_con_asignaciones': total_usuarios_con_asignaciones,
        'total_cursos_con_modulos': total_cursos_con_modulos,
        
        # Porcentajes calculados
        'tasa_completado': tasa_completado,
        'tasa_participacion': tasa_participacion,
        'tasa_finalizacion': tasa_finalizacion,
        'participacion_activa': participacion_activa,
        'cursos_con_quiz': cursos_con_quiz,
        'nivel_feedback': nivel_feedback,
        
        # Promedios calculados
        'promedio_modulos': promedio_modulos,
        'promedio_temas': promedio_temas,
        'promedio_preguntas': promedio_preguntas,
        'promedio_asignaciones': promedio_asignaciones,
        
        # NUEVAS MÉTRICAS DE DURACIÓN
        'total_horas_disponibles': total_horas_disponibles,
        'total_horas_completadas': total_horas_completadas,
        'promedio_duracion_curso': round(float(promedio_duracion_curso), 1) if promedio_duracion_curso else 0,
        'total_cursos_con_duracion': total_cursos_con_duracion,
        
        # Estado y alertas
        'sistema_activo': sistema_activo,
        'alertas': alertas,
    })
