from django.contrib import admin
from .models import Payment, PaymentLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "membership_type", "amount", "currency", "status", "created_at")
	list_filter = ("status", "membership_type", "currency", "created_at")
	search_fields = ("id", "user__email", "conversation_id", "iyzico_payment_id", "token")


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
	list_display = ("id", "payment", "event", "created_at")
	list_filter = ("event", "created_at")
	search_fields = ("payment__id", "event")
