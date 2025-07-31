#!/usr/bin/env python3
"""
Quick fix script to update the api_solicitudes function with enhanced client information
"""

import re

def fix_api_solicitudes():
    file_path = '/Users/andresrdrgz_/Documents/GitHub/PACIFICO/workflow/views_workflow.py'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Updated function content
    new_function = '''def api_solicitudes(request):
    """API para obtener solicitudes"""
    
    solicitudes = Solicitud.objects.all().select_related(
        'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a',
        'cliente', 'cotizacion'
    )
    
    # Filtro por ID específico (para obtener una solicitud)
    solicitud_id = request.GET.get('id')
    if solicitud_id:
        solicitudes = solicitudes.filter(id=solicitud_id)
    
    # Filtros
    pipeline_id = request.GET.get('pipeline')
    if pipeline_id:
        solicitudes = solicitudes.filter(pipeline_id=pipeline_id)
    
    estado = request.GET.get('estado')
    if estado == 'activas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=False)
    elif estado == 'completadas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=True)
    
    # Serializar datos
    datos = []
    for solicitud in solicitudes:
        # Obtener nombre del cliente de diferentes fuentes
        cliente_nombre = 'N/A'
        cedula_cliente = ''
        
        if solicitud.cliente:
            cliente_nombre = f"{solicitud.cliente.nombre} {solicitud.cliente.apellido}".strip()
            cedula_cliente = solicitud.cliente.cedula or ''
        elif solicitud.cotizacion and hasattr(solicitud.cotizacion, 'cliente') and solicitud.cotizacion.cliente:
            cliente_nombre = f"{solicitud.cotizacion.cliente.nombre} {solicitud.cotizacion.cliente.apellido}".strip()
            cedula_cliente = solicitud.cotizacion.cliente.cedula or ''
        elif solicitud.apc_no_cedula:
            # Fallback para solicitudes APC sin cliente asociado
            cliente_nombre = 'Cliente APC'
            cedula_cliente = solicitud.apc_no_cedula
        elif hasattr(solicitud, 'sura_no_documento') and solicitud.sura_no_documento:
            # Fallback para solicitudes SURA sin cliente asociado  
            cliente_nombre = 'Cliente SURA'
            cedula_cliente = solicitud.sura_no_documento
        
        # Datos de cotización si existe
        cotizacion_data = {}
        if solicitud.cotizacion:
            cotizacion_data = {
                'marca': getattr(solicitud.cotizacion, 'marca', ''),
                'modelo': getattr(solicitud.cotizacion, 'modelo', ''),
                'yearCarro': getattr(solicitud.cotizacion, 'year', ''),
                'valorAuto': getattr(solicitud.cotizacion, 'valor_vehiculo', ''),
                'placa': getattr(solicitud.cotizacion, 'placa', ''),
            }
        
        datos.append({
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'pipeline': solicitud.pipeline.nombre,
            'pipeline_id': solicitud.pipeline.id,
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Completada',
            'etapa_actual_id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
            'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
            'creada_por': solicitud.creada_por.username,
            'asignada_a': solicitud.asignada_a.username if solicitud.asignada_a else None,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
            
            # Información del cliente
            'cliente_nombre': cliente_nombre,
            'nombreCliente': cliente_nombre,  # Alias para compatibilidad
            'cedulaCliente': cedula_cliente,
            'apc_no_cedula': solicitud.apc_no_cedula or '',
            'apc_tipo_documento': solicitud.apc_tipo_documento or '',
            'apc_status': solicitud.apc_status or '',
            
            # Información de cotización
            **cotizacion_data,
        })
    
    return JsonResponse({'solicitudes': datos})'''
    
    # Pattern to match the first api_solicitudes function (around line 2064)
    pattern = r'def api_solicitudes\(request\):\s*"""API para obtener solicitudes"""\s*\n\s*solicitudes = Solicitud\.objects\.all\(\)\.select_related\(\s*[^}]+}\)\s*\n\s*return JsonResponse\(\{\'solicitudes\': datos\}\)'
    
    # Replace the first occurrence
    content = re.sub(pattern, new_function, content, count=1, flags=re.DOTALL)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("API function updated successfully!")

if __name__ == '__main__':
    fix_api_solicitudes()
