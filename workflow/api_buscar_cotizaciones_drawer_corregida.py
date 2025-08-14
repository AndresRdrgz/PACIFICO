from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cotizacion

@login_required
def api_buscar_cotizaciones_drawer(request):
    """API para buscar cotizaciones en el drawer - Préstamos de Auto y Personal"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'cotizaciones': []})
        
        # Base query - PRÉSTAMOS DE AUTO Y PERSONAL
        cotizaciones = Cotizacion.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query) |
            Q(id__icontains=query),
            Q(tipoPrestamo='auto') | Q(tipoPrestamo='personal')  # Incluir ambos tipos
        )
        
        # Filtrar por permisos de usuario
        if not (request.user.is_superuser or request.user.is_staff):
            # Usuarios regulares: ver sus propias cotizaciones + cotizaciones de grupos supervisados
            
            # Cotizaciones propias
            cotizaciones_propias = cotizaciones.filter(added_by=request.user)
            
            # Verificar si es supervisor de grupo
            cotizaciones_supervisadas = Cotizacion.objects.none()
            try:
                from pacifico.utils_grupos import obtener_grupos_supervisados_por_usuario
                grupos_supervisados = obtener_grupos_supervisados_por_usuario(request.user)
                
                if grupos_supervisados.exists():
                    # Obtener usuarios supervisados
                    usuarios_supervisados = []
                    for grupo_profile in grupos_supervisados:
                        miembros = grupo_profile.group.user_set.all()
                        usuarios_supervisados.extend(miembros)
                    
                    # Filtrar cotizaciones de usuarios supervisados
                    if usuarios_supervisados:
                        cotizaciones_supervisadas = cotizaciones.filter(
                            added_by__in=usuarios_supervisados
                        )
            except ImportError:
                pass  # Si no existe el módulo, continuar sin supervisión
            
            # Combinar cotizaciones propias y supervisadas
            cotizaciones = cotizaciones_propias | cotizaciones_supervisadas
        
        # Ordenar y limitar resultados
        cotizaciones = cotizaciones.order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            resultado = {
                'id': cotizacion.id,
                'nombreCliente': cotizacion.nombreCliente or 'Sin nombre',
                'cedulaCliente': cotizacion.cedulaCliente or 'Sin cédula',
                'tipoPrestamo': cotizacion.tipoPrestamo or 'Sin tipo',
                'montoFinanciado': float(cotizacion.auxMonto2) if cotizacion.auxMonto2 else 0,  # Monto Financiado
                'oficial': cotizacion.oficial or 'Sin oficial',
                'observaciones': cotizacion.observaciones or '',  # Campo observaciones
                'created_at': cotizacion.created_at.isoformat() if cotizacion.created_at else None,
                # Vehicle data for SURA auto-population
                'valorAuto': float(cotizacion.valorAuto) if cotizacion.valorAuto else None,
                'yearCarro': cotizacion.yearCarro,
                'marca': cotizacion.marca or '',
                'modelo': cotizacion.modelo or '',
                'tipoDocumento': cotizacion.tipoDocumento or 'CEDULA'
            }
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones: '{cotizacion.observaciones}'")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones type: {type(cotizacion.observaciones)}")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones length: {len(cotizacion.observaciones) if cotizacion.observaciones else 0}")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} vehicle data: valorAuto={cotizacion.valorAuto}, yearCarro={cotizacion.yearCarro}, marca={cotizacion.marca}, modelo={cotizacion.modelo}")
            resultados.append(resultado)
        
        return JsonResponse({'success': True, 'cotizaciones': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
