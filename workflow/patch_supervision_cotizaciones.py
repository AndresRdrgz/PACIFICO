# PARCHES PARA CORREGIR SUPERVISIÓN DE GRUPOS EN COTIZACIONES
# APLICAR ESTOS CAMBIOS EN workflow/views_workflow.py

# ==========================================
# PARCH 1: Primera función api_buscar_cotizaciones_drawer (línea ~2969)
# ==========================================

# BUSCAR esta línea:
#            cotizaciones = cotizaciones.filter(added_by=request.user)

# REEMPLAZARLA con:
            # Usuarios regulares: ver sus propias cotizaciones + cotizaciones de grupos supervisados
            from django.db.models import Q
            
            # Cotizaciones propias
            cotizaciones_propias = cotizaciones.filter(added_by=request.user)
            
            # Verificar si es supervisor de grupo
            cotizaciones_supervisadas = Cotizacion.objects.none()
            try:
                from pacifico.utils_grupos import obtener_grupos_supervisados_por_usuario
                grupos_supervisados = obtener_grupos_supervisados_por_usuario(request.user)
                
                if grupos_supervisados.exists():
                    print(f"🔍 DEBUG: Usuario {request.user.username} es supervisor de {grupos_supervisados.count()} grupos")
                    
                    # Obtener usuarios supervisados
                    usuarios_supervisados = []
                    for grupo_profile in grupos_supervisados:
                        miembros = grupo_profile.group.user_set.all()
                        usuarios_supervisados.extend(miembros)
                    
                    print(f"🔍 DEBUG: Usuarios supervisados encontrados: {len(usuarios_supervisados)}")
                    
                    # Filtrar cotizaciones de usuarios supervisados
                    if usuarios_supervisados:
                        cotizaciones_supervisadas = cotizaciones.filter(
                            added_by__in=usuarios_supervisados
                        )
                        print(f"🔍 DEBUG: Cotizaciones supervisadas encontradas: {cotizaciones_supervisadas.count()}")
            except ImportError as e:
                print(f"⚠️ DEBUG: No se pudo importar utils_grupos: {e}")
                pass  # Si no existe el módulo, continuar sin supervisión
            
            # Combinar cotizaciones propias y supervisadas
            cotizaciones = cotizaciones_propias | cotizaciones_supervisadas
            print(f"🔍 DEBUG: Total cotizaciones (propias + supervisadas): {cotizaciones.count()}")

# ==========================================
# PARCH 2: Segunda función api_buscar_cotizaciones_drawer (línea ~5269)
# ==========================================

# HACER EL MISMO CAMBIO en la segunda función

# ==========================================
# PARCH 3: Función nueva_solicitud (línea ~3479)
# ==========================================

# BUSCAR esta línea:
#        cotizaciones = list(cotizaciones_propias) + list(cotizaciones_supervisadas)

# REEMPLAZARLA con:
        # Combinar cotizaciones propias y supervisadas usando Q objects
        from django.db.models import Q
        if usuarios_supervisados:
            cotizaciones = Cotizacion.objects.filter(
                Q(added_by=request.user) | Q(added_by__in=usuarios_supervisados)
            ).order_by('-created_at')[:100]
        else:
            cotizaciones = cotizaciones_propias

# ==========================================
# INSTRUCCIONES DE APLICACIÓN
# ==========================================

"""
1. Abrir workflow/views_workflow.py
2. Aplicar PARCH 1 en la primera función api_buscar_cotizaciones_drawer
3. Aplicar PARCH 2 en la segunda función api_buscar_cotizaciones_drawer  
4. Aplicar PARCH 3 en la función nueva_solicitud
5. Guardar el archivo
6. Reiniciar el servidor Django
7. Probar la funcionalidad
"""
