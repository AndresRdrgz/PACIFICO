from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Celulares

# Register your models here.

@admin.register(Celulares)
class CelularesAdmin(ModelAdmin):
    pass
