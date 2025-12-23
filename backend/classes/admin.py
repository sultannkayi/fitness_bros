from django.contrib import admin
from .models import FitnessClass

#Admin panelinden görüntülemeyi kolaylaştır

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'instructor', 'date_time', 'capacity', 'is_active')
