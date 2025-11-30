from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['member', 'fitness_class', 'status', 'reserved_at']
    list_filter = ['status', 'reserved_at', 'fitness_class']
    search_fields = ['member__first_name', 'member__last_name', 'fitness_class__name']
    ordering = ['-reserved_at']
