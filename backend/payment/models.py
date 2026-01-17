from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Payment(models.Model):
	STATUS_CHOICES = [
		("pending", "Pending"),
		("success", "Success"),
		("failed", "Failed"),
		("canceled", "Canceled"),
	]

	MEMBERSHIP_CHOICES = [
		("student", "Student"),
		("standard", "Standard"),
		("premium", "Premium"),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
	membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=3, default="TRY")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

	# Iyzipay/Iyzico specific fields
	conversation_id = models.CharField(max_length=64, blank=True)
	basket_id = models.CharField(max_length=64, blank=True)
	token = models.CharField(max_length=255, blank=True)
	iyzico_payment_id = models.CharField(max_length=64, blank=True)
	raw_response = models.JSONField(blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.user_id} - {self.membership_type} - {self.amount} {self.currency} ({self.status})"


class PaymentLog(models.Model):
	payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="logs")
	event = models.CharField(max_length=32)
	payload = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.payment_id} - {self.event} - {self.created_at}"
