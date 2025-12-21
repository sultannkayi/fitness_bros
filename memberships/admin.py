from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'is_active_member')
    list_filter = ('membership_type', 'is_active_member')
    search_fields = ('user__email',)