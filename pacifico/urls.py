from django.urls import path
from .views import fideicomiso_view, login_view, main_menu, get_lineas, generate_report, cotizacion_seguro_auto
from . import views


urlpatterns = [
    path('', main_menu, name='main_menu'),
    path('fideicomiso/', fideicomiso_view, name='fideicomiso'),
    path('get_lineas/', views.get_lineas, name='get_lineas'),
    path('generate_report/', generate_report, name='generate_report'),
    path('cotizacion_seguro_auto/', cotizacion_seguro_auto, name='cotizacion_seguro_auto'),
]

