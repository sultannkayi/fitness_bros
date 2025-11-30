from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'membership_type', 'is_active', 'joined_date']
    list_filter = ['membership_type', 'is_active', 'joined_date']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']
