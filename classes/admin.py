from django.contrib import admin
from .models import FitnessClass


@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_type', 'instructor', 'schedule', 'capacity', 'price', 'is_active']
    list_filter = ['class_type', 'is_active', 'instructor']
    search_fields = ['name', 'instructor', 'description']
    ordering = ['schedule']
