from django import forms
from .models import Pregunta, Opcion
from .models import Feedback

class QuizRespuestaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        preguntas = kwargs.pop('preguntas')
        super().__init__(*args, **kwargs)

        for pregunta in preguntas:
            opciones = pregunta.opciones.all()
            
            # Campo de selección de respuesta
            self.fields[f"pregunta_{pregunta.id}"] = forms.ChoiceField(
                label=pregunta.texto,
                choices=[(opcion.id, opcion.texto) for opcion in opciones],
                widget=forms.RadioSelect,
                required=True
            )

            # Campo de comentario opcional
            self.fields[f"comentario_{pregunta.id}"] = forms.CharField(
                label="Comentario (opcional)",
                required=False,
                widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Escribe tu comentario si deseas...'})
            )

from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '¿Qué te pareció este tema?'
            }),
        }

from django import forms
from django.contrib.auth.models import User
from .models import Curso, GrupoAsignacion

class AsignacionCursoForm(forms.Form):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Selecciona usuarios"
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=GrupoAsignacion.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Selecciona grupos"
    )
    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Cursos a asignar"
    )

