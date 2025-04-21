from django import forms
from .models import Pregunta, Opcion

class RespuestaQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        preguntas = kwargs.pop('preguntas', [])
        super().__init__(*args, **kwargs)

        for pregunta in preguntas:
            field_name = f"pregunta_{pregunta.id}"

            if pregunta.tipo in ['OM', 'VF']:
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=pregunta.opciones.all(),
                    widget=forms.RadioSelect,
                    required=True,
                    label=pregunta.texto
                )
            elif pregunta.tipo == 'SM':
                self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=pregunta.opciones.all(),
                    widget=forms.CheckboxSelectMultiple,
                    required=True,
                    label=pregunta.texto
                )
            elif pregunta.tipo == 'TL':
                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea(attrs={'rows': 2}),
                    required=True,
                    label=pregunta.texto
                )
