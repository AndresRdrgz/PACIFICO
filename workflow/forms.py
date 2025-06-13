from django import forms
from django.forms import inlineformset_factory
from .models import ClienteEntrevista, OtroIngreso, ReferenciaPersonal, ReferenciaComercial

class ClienteEntrevistaForm(forms.ModelForm):
    class Meta:
        model = ClienteEntrevista
        exclude = [
            'tipo_ingreso_1', 'descripcion_ingreso_1', 'monto_ingreso_1',
            'tipo_ingreso_2', 'descripcion_ingreso_2', 'monto_ingreso_2',
        ]
        widgets = {
            # Campos de texto y fechas
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'venc_cedula': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_inicio_trabajo': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pep_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pep_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pep_fin_anterior': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pep_fam_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pep_fam_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_ext': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'imc': forms.TextInput(attrs={'class': 'form-control'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control'}),
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            'trabajo_cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'origen_fondos': forms.Select(attrs={'class': 'form-select'}),
            'cod_empleado': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_contraloria_1': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_contraloria_2': forms.TextInput(attrs={'class': 'form-control'}),
            'cod_contraloria_3': forms.TextInput(attrs={'class': 'form-control'}),
            'pep_cargo_actual': forms.TextInput(attrs={'class': 'form-control'}),
            'pep_cargo_anterior': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco_pep': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_pep': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_pep': forms.TextInput(attrs={'class': 'form-control'}),
            'institucion_pep': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_producto': forms.Select(attrs={'class': 'form-select'}),
            'oficial': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_cuenta': forms.Select(attrs={'class': 'form-select'}),
            'provincia_cedula': forms.Select(attrs={'class': 'form-select'}),
            'tipo_letra': forms.Select(attrs={'class': 'form-select'}),
            'nivel_academico': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'tipo_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'frecuencia_pago': forms.Select(attrs={'class': 'form-select'}),
            'como_se_entero': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'redes_sociales': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_completa': forms.Textarea(attrs={'class': 'form-control'}),
            'trabajo_direccion': forms.Textarea(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'casa_apto': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control'}),

            # Checkboxes (toggles)
            'autoriza_apc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'acepta_datos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_beneficiario_final': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_pep': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_familiar_pep': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OtroIngresoForm(forms.ModelForm):
    class Meta:
        model = OtroIngreso
        exclude = ['cliente']
        widgets = {
            'fuente': forms.TextInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


OtroIngresoFormSet = inlineformset_factory(
    ClienteEntrevista,
    OtroIngreso,
    form=OtroIngresoForm,
    extra=3,
    max_num=3,
    can_delete=False
)


class ReferenciaPersonalForm(forms.ModelForm):
    class Meta:
        model = ReferenciaPersonal
        fields = ['nombre', 'telefono', 'relacion', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'relacion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }


ReferenciaPersonalFormSet = inlineformset_factory(
    ClienteEntrevista,
    ReferenciaPersonal,
    form=ReferenciaPersonalForm,
    extra=3,
    max_num=3,
    can_delete=False
)


class ReferenciaComercialForm(forms.ModelForm):
    class Meta:
        model = ReferenciaComercial
        exclude = ['entrevista']
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'actividad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control'}),
        }


ReferenciaComercialFormSet = inlineformset_factory(
    ClienteEntrevista,
    ReferenciaComercial,
    form=ReferenciaComercialForm,
    extra=1,
    can_delete=True
)
