# Endpoint para obtener el JSON: http://localhost:8000/api/encuestas/

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models_encuesta import EncuestaSatisfaccionCurso
from .models import ProgresoCurso

def encuestas_json(request):
    encuestas = EncuestaSatisfaccionCurso.objects.all()
    data = [
        {
            "departamento": encuesta.departamento,
            "cargo": encuesta.cargo,
            "expositor": encuesta.expositor,
            "utilidad": encuesta.utilidad,
            "satisfaccion": encuesta.satisfaccion,
            "aprendido": encuesta.aprendido,
            "lugar": encuesta.lugar,
            "rol": encuesta.rol,
            "recomendacion": encuesta.recomendacion,
            "comentarios_curso": encuesta.comentarios_curso,
            "usuario": encuesta.usuario.username if encuesta.usuario else None,
            "nombre_usuario": encuesta.usuario.get_full_name() if encuesta.usuario else None,
            "NumeroColaborador": encuesta.usuario.username if encuesta.usuario else None,
            "nombre_curso": encuesta.curso.titulo if encuesta.curso else None,
            "Tipo de curso": encuesta.curso.get_tipo_curso_display() if encuesta.curso else None,
            "duracion_horas": encuesta.curso.duracion_horas if encuesta.curso else None,
            "fecha": encuesta.fecha,
        }
        for encuesta in encuestas
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def actualizar_progreso(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        curso_id = request.POST.get('curso_id')

        if not usuario_id or not curso_id:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        progreso = ProgresoCurso.objects.filter(usuario_id=usuario_id, curso_id=curso_id).first()
        if progreso:
            progreso.encuesta_completada = True
            progreso.save()

            # Calcular el progreso actualizado
            total_elementos = progreso.curso.modulos.count() + 1  # Incluye la encuesta
            total_completados = progreso.modulos_completados.count() + (1 if progreso.encuesta_completada else 0)
            progreso_percent = round((total_completados / total_elementos) * 100)

            return JsonResponse({
                'success': 'Progreso actualizado correctamente',
                'progreso_percent': progreso_percent,
                'redirect_url': f'/detalle_curso/{curso_id}/'
            })
        else:
            return JsonResponse({'error': 'Progreso no encontrado'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# http://127.0.0.1:8000/api/encuestas/