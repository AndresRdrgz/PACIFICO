import django_filters
from django import forms
from django.contrib.auth.models import User
from .models import Cliente

class ClienteFilter(django_filters.FilterSet):
    propietario = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username'),
        label='Propietario',
        widget=forms.SelectMultiple(attrs={
            'class': 'hidden',  # We'll hide the default widget and use our custom one
            'id': 'propietario-select'
        })
    )

    class Meta:
        model = Cliente
        fields = ['propietario']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show the filter if user is Supervisor or Administrador
        if user and (user.groups.filter(name__in=['Supervisor', 'Administrador']).exists() or user.is_superuser):
            # Keep the filter
            pass
        else:
            # Remove the filter for regular users
            self.filters.clear()
