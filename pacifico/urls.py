from django.urls import path
from .views import fideicomiso_view, login_view, main_menu
from . import views

urlpatterns = [
    path('', main_menu, name='main_menu'),
    path('fideicomiso/', fideicomiso_view, name='fideicomiso'),
    path('generate_report/', views.generate_report, name='generate_report'),
]