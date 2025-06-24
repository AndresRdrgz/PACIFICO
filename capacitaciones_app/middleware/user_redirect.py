"""
Middleware para redirección automática de usuarios con rol "Usuario" a capacitaciones_app
Autor: Sistema de Capacitaciones PACÍFICO
Fecha: Junio 22, 2025
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)


class UserRoleRedirectMiddleware:
    """
    Middleware que intercepta las requests de usuarios autenticados con rol "Usuario"
    y los redirige automáticamente a la aplicación de capacitaciones.
    
    EXCEPCIONES:
    - Usuarios STAFF: Tienen acceso libre a todo el sistema
    - Usuarios con otros roles: Acceso normal sin restricciones
    
    Flujo:
    1. Usuario con rol "Usuario" (no staff) hace login
    2. Intenta acceder a cualquier URL del sistema
    3. Middleware intercepta y redirige a /cursos/
    4. Usuario queda restringido solo a capacitaciones_app
    """
    
    def __init__(self, get_response):
        """
        Inicialización del middleware
        """
        self.get_response = get_response
          # URLs que están permitidas para usuarios con rol "Usuario"
        self.allowed_paths = [
            '/cursos/',           # App de capacitaciones
            '/perfil/',           # Perfil de usuario
            '/logout/',           # Logout
            '/accounts/logout/',  # Logout alternativo
            '/admin/logout/',     # Logout admin
            '/static/',           # Archivos estáticos
            '/media/',            # Archivos de media
        ]
          # URLs que NO deben ser interceptadas (evitar loops)
        self.exempt_paths = [
            '/admin/login/',      # Login del admin
            '/accounts/login/',   # Login
            '/login/',            # Login alternativo
        ]

    def __call__(self, request):
        """
        Procesa cada request que llega al sistema
        """
        # Procesar la request antes de pasarla a la view
        redirect_response = self.process_request(request)
        if redirect_response:
            return redirect_response
              # Si no hay redirección, continuar normalmente
        response = self.get_response(request)
        return response

    def process_request(self, request):
        """
        Intercepta las requests antes de que lleguen a las views
        """
        # Solo procesar usuarios autenticados
        if not request.user.is_authenticated:
            return None
            
        # Si el usuario es STAFF, permitir acceso libre a todo el sistema
        if request.user.is_staff:
            logger.info(f"Usuario staff '{request.user.username}' tiene acceso libre al sistema")
            return None
            
        # Verificar si el usuario tiene UserProfile con rol "Usuario"
        try:
            user_profile = request.user.userprofile
            user_role = user_profile.rol
        except:
            # Si no tiene UserProfile o hay error, permitir acceso normal
            return None
            
        # Solo procesar usuarios con rol "Usuario" (no staff)
        if user_role != 'Usuario':
            return None
            
        # Obtener la URL actual
        current_path = request.path
        
        # No interceptar URLs exentas (login, logout, etc.)
        for exempt_path in self.exempt_paths:
            if current_path.startswith(exempt_path):
                return None
                
        # Verificar si ya está en una URL permitida
        for allowed_path in self.allowed_paths:
            if current_path.startswith(allowed_path):
                return None
                
        # Si llegó hasta aquí, es un usuario con rol "Usuario" 
        # intentando acceder a una URL no permitida
        logger.info(f"Redirigiendo usuario '{request.user.username}' con rol 'Usuario' desde '{current_path}' hacia '/cursos/'")
        
        # Redirigir a capacitaciones
        return HttpResponseRedirect('/cursos/')
