from django import forms
from .models import DebidaDiligencia

class DebidaDiligenciaForm(forms.ModelForm):
    class Meta:
        model = DebidaDiligencia
        fields = ['busqueda_google', 'busqueda_registro_publico', 'comentarios']
        widgets = {
            'busqueda_google': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'busqueda_registro_publico': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comentarios u observaciones adicionales (opcional)'
            })
        }
        labels = {
            'busqueda_google': 'Búsqueda Google',
            'busqueda_registro_publico': 'Búsqueda Registro Público',
            'comentarios': 'Comentarios/Observaciones'
        }
        help_texts = {
            'busqueda_google': 'Suba un archivo PDF o imagen (PNG, JPG, JPEG) con los resultados de la búsqueda en Google.',
            'busqueda_registro_publico': 'Suba un archivo PDF o imagen (PNG, JPG, JPEG) con los resultados de la búsqueda en Registro Público.',
            'comentarios': 'Agregue cualquier comentario u observación adicional sobre la debida diligencia.'
        }
