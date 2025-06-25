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
   
)

# Vista adicional para perfil de usuario
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.messages import get_messages
from pacifico.models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def custom_logout(request):
    """Vista personalizada de logout que limpia los mensajes antes de cerrar sesión"""
    # Limpiar todos los mensajes de la sesión
    storage = get_messages(request)
    for message in storage:
        pass  # Esto consume todos los mensajes
    storage.used = True
    
    # Realizar logout
    logout(request)
    
    # Redirigir al login
    return redirect('/accounts/login/')

@login_required
def perfil_usuario(request):
    """Vista simple para mostrar y editar el perfil del usuario y cambiar contraseña"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    password_form = PasswordChangeForm(user=request.user)
    show_password_form = False

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            messages.success(request, '✅ Foto de perfil actualizada correctamente')
            return redirect('perfil_usuario')
        elif 'old_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            show_password_form = True
            if password_form.is_valid():
                try:
                    user = password_form.save()
                    update_session_auth_hash(request, user)  # Mantener sesión activa
                    messages.success(request, '🔒 ¡Contraseña actualizada exitosamente! Tu sesión se mantuvo activa.')
                    return redirect('perfil_usuario')
                except Exception as e:
                    messages.error(request, f'❌ Error inesperado al cambiar la contraseña: {str(e)}')
            else:
                # Mensajes específicos para diferentes tipos de errores
                if password_form.errors.get('old_password'):
                    messages.error(request, '❌ La contraseña actual es incorrecta.')
                elif password_form.errors.get('new_password2'):
                    messages.error(request, '❌ Las nuevas contraseñas no coinciden.')
                elif password_form.errors.get('new_password1'):
                    messages.error(request, '❌ La nueva contraseña no cumple con los requisitos de seguridad.')
                else:
                    messages.error(request, '❌ Por favor corrige los errores en el formulario.')

    context = {
        'user_profile': user_profile,
        'password_form': password_form,
        'show_password_form': show_password_form,
    }
    return render(request, 'capacitaciones_app/perfil_usuario.html', context)

@login_required
def validacion_ui(request):
    """Vista para validar visualmente los componentes modernizados de la UI"""
    return render(request, 'capacitaciones_app/validacion_ui.html')

