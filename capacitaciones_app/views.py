# capacitaciones_app/views.py

# Este archivo importa todas las vistas organizadas en archivos separados
from .views_cursos import (
    lista_cursos,
    detalle_curso,
    ver_tema,
    marcar_tema_completado,
)

from .views_quiz import (
    quiz_modulo,
)

from .views_certificados import (
    certificado,
)

from .views_asignacion import (
    asignacion_admin,
    asignar_curso_ajax,
    desasignar_curso_ajax,
    cursos_asignados_ajax,
    miembros_grupo_ajax,
    exportar_asignaciones_excel,
    usuarios_grupo_ajax,         # <-- agregar
    quitar_usuario_grupo_ajax,   # <-- agregar
)

# Vista adicional para perfil de usuario
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pacifico.models import UserProfile

@login_required
def perfil_usuario(request):
    """Vista simple para mostrar y editar el perfil del usuario"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Actualizar foto de perfil si se envía
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            messages.success(request, '✅ Foto de perfil actualizada correctamente')
            return redirect('perfil_usuario')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'capacitaciones_app/perfil_usuario.html', context)

@login_required
def validacion_ui(request):
    """Vista para validar visualmente los componentes modernizados de la UI"""
    return render(request, 'capacitaciones_app/validacion_ui.html')

