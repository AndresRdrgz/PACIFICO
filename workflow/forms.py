from django import forms
from django.forms import modelformset_factory
from .models import ClienteEntrevista, OtroIngreso, ReferenciaPersonal, ReferenciaComercial
from .modelsWorkflow import Solicitud

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

    peso = forms.DecimalField(
        required=True,
        label='Peso (lb)',
        min_value=0,
        decimal_places=2,
        max_digits=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    estatura = forms.DecimalField(
        required=True,
        label='Estatura (m)',
        min_value=0,
        decimal_places=2,
        max_digits=4,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
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
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatura': forms.NumberInput(attrs={'class': 'form-control'}),

            # Checkboxes (toggles)
            'autoriza_apc': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': 'VERDADERO'}),
            'acepta_datos': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': 'VERDADERO'}),
            'es_beneficiario_final': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': 'VERDADERO'}),
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
        # Asegura que los toggles de autorizaciones sean booleanos según el valor recibido
        for field in ['autoriza_apc', 'acepta_datos', 'es_beneficiario_final']:
            val = self.data.get(field)
            # El valor será 'VERDADERO' si el toggle está encendido, 'FALSO' o None si está apagado
            cleaned_data[field] = (val == 'VERDADERO')
        # PEP toggles
        for field in ['es_pep', 'es_familiar_pep']:
            val = self.data.get(field)
            cleaned_data[field] = bool(val)
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

ETIQUETAS_CHOICES = [
    ("", "-"),
    ("📞 No responde", "📞 No responde"),
    ("🗓️ Cita agendada", "🗓️ Cita agendada"),
    ("✅ Documentos completos", "✅ Documentos completos"),
    ("📎 Falta carta trabajo", "📎 Falta carta trabajo"),
    ("🔄 Seguimiento en 48h", "🔄 Seguimiento en 48h"),
    ("💬 WhatsApp activo", "💬 WhatsApp activo"),
    ("⚠️ Cliente indeciso", "⚠️ Cliente indeciso"),
    ("🚀 Cliente caliente", "🚀 Cliente caliente"),
    ("🕐 Esperando confirmación", "🕐 Esperando confirmación"),
    ("🧾 Enviado a crédito", "🧾 Enviado a crédito"),
    ("🔒 En validación", "🔒 En validación"),
    ("❌ Caso descartado", "❌ Caso descartado"),
]

class SolicitudAdminForm(forms.ModelForm):
    etiquetas_oficial = forms.ChoiceField(
        choices=ETIQUETAS_CHOICES,
        required=False,
        widget=forms.Select()
    )

    class Meta:
        model = Solicitud
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.etiquetas_oficial:
            self.fields['etiquetas_oficial'].initial = self.instance.etiquetas_oficial

    def clean_etiquetas_oficial(self):
        data = self.cleaned_data['etiquetas_oficial']
        return data or ''


# ==========================================
# FORMULARIO WEB CANAL DIGITAL
# ==========================================

from .models import FormularioWeb

class FormularioWebForm(forms.ModelForm):
    """Formulario para capturar solicitudes del canal digital"""
    
    class Meta:
        model = FormularioWeb
        fields = [
            'nombre',
            'apellido',
            'cedulaCliente',
            'celular',
            'correo_electronico',
            'fecha_nacimiento',
            'sexo',
            'sector',
            'salario',
            'producto_interesado',
            'dinero_a_solicitar',
            'autorizacion_apc',
            'acepta_condiciones',
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'Ingrese sus nombres'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'Ingrese sus apellidos'
            }),
            'cedulaCliente': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'Ejemplo: 8-888-8888'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'Ejemplo: 6000-0000'
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'ejemplo@correo.com'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'type': 'date'
            }),
            'sexo': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm'
            }),
            'sector': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm'
            }),
            'salario': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm'
            }),
            'producto_interesado': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm'
            }),
            'dinero_a_solicitar': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'Ejemplo: 5000.00',
                'step': '0.01'
            }),
            'autorizacion_apc': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500'
            }),
            'acepta_condiciones': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos requeridos
        self.fields['nombre'].required = True
        self.fields['apellido'].required = True
        self.fields['cedulaCliente'].required = True
        self.fields['celular'].required = True
        self.fields['correo_electronico'].required = True
        self.fields['fecha_nacimiento'].required = True
        self.fields['sexo'].required = True
        self.fields['sector'].required = True
        self.fields['salario'].required = True
        self.fields['producto_interesado'].required = True
        self.fields['autorizacion_apc'].required = True
        self.fields['acepta_condiciones'].required = True
        
        # Campo condicional
        self.fields['dinero_a_solicitar'].required = False
        
        # Etiquetas personalizadas
        self.fields['cedulaCliente'].label = 'Cédula'
        self.fields['correo_electronico'].label = 'Correo Electrónico'
        self.fields['fecha_nacimiento'].label = 'Fecha de Nacimiento'
        self.fields['dinero_a_solicitar'].label = 'Dinero a Solicitar'
        self.fields['autorizacion_apc'].label = '¿Nos autorizas a revisar tu APC? (Artículo 23 de la ley 24 del 22 de mayo del 2022)'
        self.fields['acepta_condiciones'].label = 'Acepto permitir a Pacífico Préstamos almacenar y procesar mis datos personales (Ley 81 del 2019 y su reglamentación).'

    def clean_cedulaCliente(self):
        """Validación para el formato de cédula"""
        cedula = self.cleaned_data.get('cedulaCliente')
        if cedula:
            # VALIDACIÓN DE CÉDULA ÚNICA DESHABILITADA - Permite cédulas repetidas
            # if FormularioWeb.objects.filter(cedulaCliente=cedula).exists():
            #     raise forms.ValidationError('Ya existe una solicitud con esta cédula.')
            pass
        return cedula

    def clean_correo_electronico(self):
        """Validación adicional para el correo electrónico"""
        email = self.cleaned_data.get('correo_electronico')
        if email:
            # Validar formato básico (ya se hace por EmailField)
            import re
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                raise forms.ValidationError('Formato de correo electrónico incorrecto.')
        return email

    def clean(self):
        """Validaciones globales del formulario"""
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto_interesado')
        dinero = cleaned_data.get('dinero_a_solicitar')
        
        # Si el producto es "Préstamos personal", el dinero es requerido
        if producto == 'Préstamos personal' and not dinero:
            raise forms.ValidationError({
                'dinero_a_solicitar': 'Este campo es requerido para préstamos personales.'
            })
        
        # Validar autorizaciones
        if not cleaned_data.get('autorizacion_apc'):
            raise forms.ValidationError({
                'autorizacion_apc': 'Debe autorizar la revisión de APC para continuar.'
            })
            
        if not cleaned_data.get('acepta_condiciones'):
            raise forms.ValidationError({
                'acepta_condiciones': 'Debe aceptar las condiciones para continuar.'
            })
        
        return cleaned_data