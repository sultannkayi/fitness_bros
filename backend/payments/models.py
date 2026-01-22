from django.db import models
from django.conf import settings
from memberships.models import Member
from decimal import Decimal


class MembershipPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
        ('cancelled', 'İptal Edildi'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='membership_payments'
    )
    new_membership_type = models.CharField(
        max_length=20,
        choices=Member.MEMBERSHIP_CHOICES,
        verbose_name="Yeni Üyelik Tipi"
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Ödenen Tutar"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Ödeme Durumu"
    )
    iyzico_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Iyzico İşlem ID"
    )
    iyzico_conversation_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Iyzico Konuşma ID (Callback için)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Üyelik Ödemesi"
        verbose_name_plural = "Üyelik Ödemeleri"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.member.user.email} - {self.new_membership_type} - {self.amount} TL ({self.status})"

    def save(self, *args, **kwargs):
        if self.pk is None:  # Yeni kayıt ise
            # Tutarı settings'den otomatik çek (eğer elle girilmediyse)
            if self.amount == 0 or self.amount is None:
                self.amount = settings.MEMBERSHIP_PRICES.get(self.new_membership_type, Decimal('0.00'))
        super().save(*args, **kwargs)