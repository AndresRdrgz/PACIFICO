import django_filters
from django import forms
from .models import Cotizacion

class CotizacionFilter(django_filters.FilterSet):
    created_at__date__gte = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
        label='Fecha Desde',
        widget=forms.DateInput(
            attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'type': 'date'
            }
        )
    )
    created_at__date__lte = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
        label='Fecha Hasta',
        widget=forms.DateInput(
            attrs={
                'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
                'type': 'date'
            }
        )
        
        )
    oficial = django_filters.ChoiceFilter(
        field_name='oficial',
        lookup_expr='exact',
        label='Oficial',
        choices=[],  # Se poblarán dinámicamente
        empty_label='TODAS',
        widget=forms.Select(
            attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            "max_length":"100"
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar las opciones dinámicamente
        try:
            oficiales = Cotizacion.objects.values_list('oficial', flat=True).distinct()
            self.filters['oficial'].extra['choices'] = [(oficial, oficial) for oficial in oficiales if oficial]
        except Exception:
            # Si hay error de conexión, usar lista vacía
            self.filters['oficial'].extra['choices'] = []
    marca = django_filters.ChoiceFilter(
        field_name='marca',
        lookup_expr='exact',
        label='Marca',
        choices=[(marca, marca) for marca in Cotizacion.objects.values_list('marca', flat=True).distinct()],
        empty_label='TODAS',
        widget=forms.Select(
            attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            "max_length":"100"
            }
        )
    )
    tipoPrestamo = django_filters.ChoiceFilter(
        field_name='tipoPrestamo',
        lookup_expr='exact',
        label='Tipo de Prestamo',
        choices=[('auto', 'auto'), ('personal', 'personal')],
        empty_label='TODAS',
        widget=forms.Select(
            attrs={
            'class': 'w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-blue-500 hover:border-gray-300 shadow-sm focus:shadow',
            "max_length":"100"
            }
        )
    )

    class Meta:
        model = Cotizacion
        fields = ['created_at__date__gte', 'created_at__date__lte', 'oficial','marca']
        