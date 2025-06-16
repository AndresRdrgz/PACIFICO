from django import forms
from django.forms import modelformset_factory
from .models import ClienteEntrevista, OtroIngreso, ReferenciaPersonal, ReferenciaComercial

class ClienteEntrevistaForm(forms.ModelForm):
    JUBILADO_CHOICES = (
        ('True', 'Sí'),
        ('False', 'No'),
    )
    jubilado = forms.ChoiceField(
        choices=JUBILADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Jubilado'
    )

    provincia_cedula = forms.ChoiceField(
        choices=ClienteEntrevista._meta.get_field('provincia_cedula').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Provincia de la cédula'
    )
    tipo_letra = forms.ChoiceField(
        choices=ClienteEntrevista._meta.get_field('tipo_letra').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Letra de la cédula'
    )

    tipo_ingreso_1 = forms.CharField(required=False, label='Tipo de Ingreso 1')
    descripcion_ingreso_1 = forms.CharField(required=False, label='Descripción Ingreso 1')
    monto_ingreso_1 = forms.DecimalField(required=False, label='Monto Ingreso 1', min_value=0, decimal_places=2, max_digits=12)

    tipo_ingreso_2 = forms.CharField(required=False, label='Tipo de Ingreso 2')
    descripcion_ingreso_2 = forms.CharField(required=False, label='Descripción Ingreso 2')
    monto_ingreso_2 = forms.DecimalField(required=False, label='Monto Ingreso 2', min_value=0, decimal_places=2, max_digits=12)

    tipo_ingreso_3 = forms.CharField(required=False, label='Tipo de Ingreso 3')
    descripcion_ingreso_3 = forms.CharField(required=False, label='Descripción Ingreso 3')
    monto_ingreso_3 = forms.DecimalField(required=False, label='Monto Ingreso 3', min_value=0, decimal_places=2, max_digits=12)

    tel_ext = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ClienteEntrevista
        exclude = [
            # No excluyas ningún campo relevante aquí
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
            'tel_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_ext': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
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
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_completa': forms.Textarea(attrs={'class': 'form-control'}),
            'trabajo_direccion': forms.Textarea(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'casa_apto': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            # Checkboxes (toggles)
            'autoriza_apc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'acepta_datos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_beneficiario_final': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # PEP toggles con estilo Bootstrap 5 Switch y tamaño personalizado
            'es_pep': forms.CheckboxInput(attrs={
                'class': 'form-check-input form-switch',
                'style': 'width:2.5em;height:1.5em;',
                'role': 'switch'
            }),
            'es_familiar_pep': forms.CheckboxInput(attrs={
                'class': 'form-check-input form-switch',
                'style': 'width:2.5em;height:1.5em;',
                'role': 'switch'
            }),
            'conyuge_nombre': forms.TextInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Nombre completo',
            }),
            'conyuge_cedula': forms.TextInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Cédula',
            }),
            'conyuge_telefono': forms.TextInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Teléfono',
            }),
            'conyuge_empresa': forms.TextInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Empresa',
            }),
            'conyuge_lugar_trabajo': forms.TextInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Lugar de trabajo',
            }),
            'conyuge_cargo': forms.TextInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Cargo',
            }),
            'conyuge_ingreso': forms.NumberInput(attrs={
                'class': 'flex-1 outline-none bg-transparent',
                'placeholder': 'Ingreso mensual',
                'step': '0.01',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Asegura que los toggles (checkboxes) se guarden como booleanos
        for field in ['autoriza_apc', 'acepta_datos', 'es_beneficiario_final', 'es_pep', 'es_familiar_pep']:
            cleaned_data[field] = bool(self.data.get(field, False))
        return cleaned_data

    def clean_jubilado(self):
        value = self.cleaned_data['jubilado']
        return value == 'True'

    def clean_es_pep(self):
        return bool(self.cleaned_data.get('es_pep', False))

    def clean_es_familiar_pep(self):
        return bool(self.cleaned_data.get('es_familiar_pep', False))


class OtroIngresoForm(forms.ModelForm):
    TIPO_INGRESO_CHOICES = [
        ('', '---------'),
        ('LOCAL', 'LOCAL'),
        ('EXTRANJERO', 'EXTRANJERO'),
    ]
    tipo_ingreso = forms.ChoiceField(
        choices=TIPO_INGRESO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Ingreso'
    )

    fuente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    monto = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    class Meta:
        model = OtroIngreso
        exclude = ['cliente']
        widgets = {
            # 'fuente' y 'monto' ya definidos arriba, así que puedes omitirlos aquí
        }


OtroIngresoFormSet = modelformset_factory(
    OtroIngreso,
    form=OtroIngresoForm,
    extra=3,
    max_num=3,
    can_delete=True
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


ReferenciaPersonalFormSet = modelformset_factory(
    ReferenciaPersonal,
    form=ReferenciaPersonalForm,
    extra=3,
    max_num=3,
    can_delete=True
)

class ReferenciaComercialForm(forms.ModelForm):
    TIPO_CHOICES = [
        ('', '---------'),
        ('COMERCIAL', 'COMERCIAL'),
        ('CLIENTES', 'CLIENTES'),
    ]
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo'
    )
    nombre = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = ReferenciaComercial
        exclude = ['entrevista']
        widgets = {
            'actividad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control'}),
        }


ReferenciaComercialFormSet = modelformset_factory(
    ReferenciaComercial,
    form=ReferenciaComercialForm,
    extra=1,
    can_delete=True
)