from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelform_factory
from django.forms import inlineformset_factory
from .models import ClienteEntrevista, OtroIngreso, ReferenciaPersonal, ReferenciaComercial
from .forms import (
    ClienteEntrevistaForm,
    OtroIngresoFormSet,
    ReferenciaPersonalFormSet,
    ReferenciaComercialFormSet,
)
from django.http import HttpResponse
from django.contrib import messages
import openpyxl
from openpyxl.utils import get_column_letter
import datetime
import csv


def entrevista_cliente_view(request):
    steps_info = [
        ("Datos Generales", "fa-user"),
        ("Dirección", "fa-location-dot"),
        ("Cónyuge", "fa-people-roof"),
        ("Laboral", "fa-briefcase"),
        ("PEP", "fa-shield-halved"),
        ("Ref. Pers.", "fa-user-group"),
        ("Ref. Com.", "fa-building"),
        ("Bancarios", "fa-university"),
        ("Autorizaciones", "fa-circle-check"),
    ]


    if request.method == 'POST':
        form = ClienteEntrevistaForm(request.POST, request.FILES)
        referencias_formset = ReferenciaPersonalFormSet(request.POST, prefix='personales')
        referencias_comerciales_formset = ReferenciaComercialFormSet(request.POST, prefix='comerciales')
        otros_ingresos_formset = OtroIngresoFormSet(request.POST, prefix='otrosingresos')

        if (
            form.is_valid() and
            referencias_formset.is_valid() and
            referencias_comerciales_formset.is_valid() and
            otros_ingresos_formset.is_valid()
        ):
            entrevista = form.save()

            # Relaciona correctamente las referencias personales con la entrevista
            referencias_formset.instance = entrevista
            referencias_formset.save()

            referencias_comerciales_formset.instance = entrevista
            referencias_comerciales_formset.save()

            otros_ingresos_formset.instance = entrevista
            otros_ingresos_formset.save()

            # Elimina otros ingresos vacíos
            for form_ing in otros_ingresos_formset:
                if not form_ing.cleaned_data.get('fuente') and not form_ing.cleaned_data.get('monto'):
                    if form_ing.instance.pk:
                        form_ing.instance.delete()

            return redirect('formulario_gracias')

    else:
        form = ClienteEntrevistaForm()
        entrevista_nueva = ClienteEntrevista()
        referencias_formset = ReferenciaPersonalFormSet(
            instance=entrevista_nueva,
            queryset=ReferenciaPersonal.objects.none(),
            prefix='personales'
        )
        referencias_comerciales_formset = ReferenciaComercialFormSet(instance=entrevista_nueva, queryset=ReferenciaComercial.objects.none(), prefix='comerciales')
        otros_ingresos_formset = OtroIngresoFormSet(queryset=OtroIngreso.objects.none(), prefix='otrosingresos')

    return render(request, 'formulario/entrevista_cliente.html', {
        'form': form,
        'referencias_formset': referencias_formset,
        'referencias_comerciales_formset': referencias_comerciales_formset,
        'otros_ingresos_formset': otros_ingresos_formset,
        'steps_info': steps_info,
        'messages': messages.get_messages(request)
    })


def gracias(request):
    return render(request, 'formulario/gracias.html')


def lista_entrevistas(request):
    entrevistas = ClienteEntrevista.objects.all()
    return render(request, 'formulario/lista_entrevistas.html', {'entrevistas': entrevistas})


def descargar_entrevistas_excel(request):
    entrevistas = ClienteEntrevista.objects.all()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    ws_entrevistas = wb.create_sheet(title="Entrevistas")
    campos_entrevista = [field.name for field in ClienteEntrevista._meta.fields]
    ws_entrevistas.append(campos_entrevista)

    for entrevista in entrevistas:
        fila = []
        for field in campos_entrevista:
            valor = getattr(entrevista, field)
            if isinstance(valor, datetime.datetime) and valor.tzinfo is not None:
                valor = valor.replace(tzinfo=None)
            fila.append(valor if valor is not None else "")
        ws_entrevistas.append(fila)

    ws_ref_personales = wb.create_sheet(title="Referencias Personales")
    campos_ref_personal = ['entrevista_id', 'nombre', 'telefono', 'relacion', 'direccion']
    ws_ref_personales.append(campos_ref_personal)

    for entrevista in entrevistas:
        for ref in entrevista.referencias_personales.all():
            fila = [entrevista.id, ref.nombre, ref.telefono, ref.relacion, ref.direccion]
            ws_ref_personales.append(fila)

    ws_ref_comerciales = wb.create_sheet(title="Referencias Comerciales")
    campos_ref_comercial = ['entrevista_id', 'tipo', 'nombre', 'actividad', 'telefono', 'celular', 'saldo']
    ws_ref_comerciales.append(campos_ref_comercial)

    for entrevista in entrevistas:
        for ref in entrevista.referencias_comerciales.all():
            fila = [entrevista.id, ref.tipo, ref.nombre, ref.actividad, ref.telefono, ref.celular, ref.saldo]
            ws_ref_comerciales.append(fila)

    ws_otros_ingresos = wb.create_sheet(title="Otros Ingresos")
    campos_otros_ingresos = ['cliente_id', 'fuente', 'monto']
    ws_otros_ingresos.append(campos_otros_ingresos)

    for entrevista in entrevistas:
        for ingreso in entrevista.otros_ingresos.all():
            fila = [entrevista.id, ingreso.fuente, ingreso.monto]
            ws_otros_ingresos.append(fila)

    for ws in [ws_entrevistas, ws_ref_personales, ws_ref_comerciales, ws_otros_ingresos]:
        for col_num, column_cells in enumerate(ws.columns, 1):
            max_length = 0
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = max_length + 2
            ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=entrevistas_completas.xlsx'
    wb.save(response)
    return response


def descargar_entrevista_excel(request, entrevista_id):
    entrevista = ClienteEntrevista.objects.get(pk=entrevista_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="entrevista_{entrevista_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Campo', 'Valor'])

    for field in entrevista._meta.fields:
        writer.writerow([field.verbose_name, getattr(entrevista, field.name)])

    writer.writerow([])
    writer.writerow(['Referencias Personales'])
    for ref in entrevista.referencias_personales.all():
        writer.writerow([ref.nombre, ref.direccion, ref.relacion, '', '', '', ''])

    writer.writerow([])
    writer.writerow(['Referencias Comerciales'])
    for ref in entrevista.referencias_comerciales.all():
        writer.writerow([ref.nombre, ref.tipo, ref.actividad, ref.telefono, ref.celular, ref.saldo])

    writer.writerow([])
    writer.writerow(['Otros Ingresos'])
    for ingreso in entrevista.otros_ingresos.all():
        writer.writerow([ingreso.fuente, '', ingreso.monto])

    return response


def cliente_entrevista_create(request):
    if request.method == 'POST':
        form = ClienteEntrevistaForm(request.POST)
        otro_ingreso_formset = OtroIngresoFormSet(request.POST, prefix='otroingreso')
        referencia_personal_formset = ReferenciaPersonalFormSet(request.POST, prefix='refpersonal')
        referencia_comercial_formset = ReferenciaComercialFormSet(request.POST, prefix='refcomercial')
        if (form.is_valid() and otro_ingreso_formset.is_valid() and
                referencia_personal_formset.is_valid() and referencia_comercial_formset.is_valid()):
            cliente = form.save()
            otro_ingreso_formset.instance = cliente
            otro_ingreso_formset.save()
            referencia_personal_formset.instance = cliente
            referencia_personal_formset.save()
            referencia_comercial_formset.instance = cliente
            referencia_comercial_formset.save()
            return redirect('cliente_entrevista_detail', pk=cliente.pk)
    else:
        form = ClienteEntrevistaForm()
        otro_ingreso_formset = OtroIngresoFormSet(prefix='otroingreso')
        referencia_personal_formset = ReferenciaPersonalFormSet(prefix='refpersonal')
        referencia_comercial_formset = ReferenciaComercialFormSet(prefix='refcomercial')
    return render(request, 'workflow/cliente_entrevista_form.html', {
        'form': form,
        'otro_ingreso_formset': otro_ingreso_formset,
        'referencia_personal_formset': referencia_personal_formset,
        'referencia_comercial_formset': referencia_comercial_formset,
    })


def cliente_entrevista_detail(request, pk):
    cliente = get_object_or_404(ClienteEntrevista, pk=pk)
    return render(request, 'workflow/cliente_entrevista_detail.html', {'cliente': cliente})


def cliente_entrevista_list(request):
    clientes = ClienteEntrevista.objects.all()
    return render(request, 'workflow/cliente_entrevista_list.html', {'clientes': clientes})


# Validaciones actuales en entrevista_cliente_view:

# 1. ClienteEntrevistaForm:
#    - Se valida con form.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 2. ReferenciaPersonalFormSet:
#    - Se valida con referencias_formset.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 3. ReferenciaComercialFormSet:
#    - Se valida con referencias_comerciales_formset.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 4. OtroIngresoFormSet:
#    - Se valida con otros_ingresos_formset.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 5. Solo si TODOS los formularios y formsets son válidos:
#    - Se guarda la instancia principal (ClienteEntrevista).
#    - Se guardan todas las referencias personales asociadas.
#    - Se guardan todas las referencias comerciales asociadas.
#    - Se guardan todos los otros ingresos asociados.
#
# 6. Si algún formulario o formset no es válido:
#    - El usuario ve los errores en pantalla y no se guarda nada en la base de datos.
#
# 7. Los campos requeridos y validaciones de tipo/dominio se definen en los modelos y en los formularios Django.
#
# 8. Los formsets permiten agregar/eliminar múltiples referencias y otros ingresos, y validan la estructura de cada uno.
#
# 9. El botón "Enviar" solo redirige a la página de gracias si todo es válido y guardado.
#    - Se valida con otros_ingresos_formset.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 5. Solo si TODOS los formularios y formsets son válidos:
#    - Se guarda la instancia principal (ClienteEntrevista).
#    - Se guardan todas las referencias personales asociadas.
#    - Se guardan todas las referencias comerciales asociadas.
#    - Se guardan todos los otros ingresos asociados.
#
# 6. Si algún formulario o formset no es válido:
#    - El usuario ve los errores en pantalla y no se guarda nada en la base de datos.
#
# 7. Los campos requeridos y validaciones de tipo/dominio se definen en los modelos y en los formularios Django.
#
# 8. Los formsets permiten agregar/eliminar múltiples referencias y otros ingresos, y validan la estructura de cada uno.
#
# 9. El botón "Enviar" solo redirige a la página de gracias si todo es válido y guardado.
# 4. OtroIngresoFormSet:
#    - Se valida con otros_ingresos_formset.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 5. Solo si TODOS los formularios y formsets son válidos:
#    - Se guarda la instancia principal (ClienteEntrevista).
#    - Se guardan todas las referencias personales asociadas.
#    - Se guardan todas las referencias comerciales asociadas.
#    - Se guardan todos los otros ingresos asociados.
#
# 6. Si algún formulario o formset no es válido:
#    - El usuario ve los errores en pantalla y no se guarda nada en la base de datos.
#
# 7. Los campos requeridos y validaciones de tipo/dominio se definen en los modelos y en los formularios Django.
#
# 8. Los formsets permiten agregar/eliminar múltiples referencias y otros ingresos, y validan la estructura de cada uno.
#
# 9. El botón "Enviar" solo redirige a la página de gracias si todo es válido y guardado.
#    - Se valida con otros_ingresos_formset.is_valid().
#    - Si no es válido, se muestran los errores en el template.
#
# 5. Solo si TODOS los formularios y formsets son válidos:
#    - Se guarda la instancia principal (ClienteEntrevista).
#    - Se guardan todas las referencias personales asociadas.
#    - Se guardan todas las referencias comerciales asociadas.
#    - Se guardan todos los otros ingresos asociados.
#
# 6. Si algún formulario o formset no es válido:
#    - El usuario ve los errores en pantalla y no se guarda nada en la base de datos.
#
# 7. Los campos requeridos y validaciones de tipo/dominio se definen en los modelos y en los formularios Django.
#
# 8. Los formsets permiten agregar/eliminar múltiples referencias y otros ingresos, y validan la estructura de cada uno.
#
# 9. El botón "Enviar" solo redirige a la página de gracias si todo es válido y guardado.
# 9. El botón "Enviar" solo redirige a la página de gracias si todo es válido y guardado.
