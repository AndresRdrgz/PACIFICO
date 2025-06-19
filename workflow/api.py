from django.http import JsonResponse
from .models import ClienteEntrevista

def entrevistas_json(request):
    entrevistas = ClienteEntrevista.objects.all()
    data = []
    for entrevista in entrevistas:
        # Excluye lugar_nacimiento y asegura nacionalidad
        registro = {field.name: getattr(entrevista, field.name) for field in ClienteEntrevista._meta.fields if field.name != 'lugar_nacimiento'}
        if 'nacionalidad' not in registro:
            registro['nacionalidad'] = getattr(entrevista, 'nacionalidad', None)
        # Relacionados: Otros Ingresos
        registro['otros_ingresos'] = [
            {
                'tipo_ingreso': oi.tipo_ingreso,
                'fuente': oi.fuente,
                'monto': float(oi.monto) if oi.monto is not None else None
            }
            for oi in entrevista.otros_ingresos.all()
        ]
        # Relacionados: Referencias Personales
        registro['referencias_personales'] = [
            {
                'nombre': rp.nombre,
                'telefono': rp.telefono,
                'relacion': rp.relacion,
                'direccion': rp.direccion
            }
            for rp in entrevista.referencias_personales.all()
        ]
        # Relacionados: Referencias Comerciales
        registro['referencias_comerciales'] = [
            {
                'tipo': rc.tipo,
                'nombre': rc.nombre,
                'actividad': rc.actividad,
                'telefono': rc.telefono,
                'celular': rc.celular,
                'saldo': float(rc.saldo) if rc.saldo is not None else None
            }
            for rc in entrevista.referencias_comerciales.all()
        ]
        # Conversión explícita para decimales (peso, estatura)
        if 'peso' in registro and registro['peso'] is not None:
            registro['peso'] = float(registro['peso'])
        if 'estatura' in registro and registro['estatura'] is not None:
            registro['estatura'] = float(registro['estatura'])

        data.append(registro)
    response = {
        "status": "success",
        "total": len(data),
        "data": data
    }
    return JsonResponse(response, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})
