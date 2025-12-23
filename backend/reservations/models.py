from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from memberships.services import PricingEngine

class Reservation(models.Model):
    member = models.ForeignKey(
        'memberships.Member',
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    fitness_class = models.ForeignKey(
        'classes.FitnessClass',
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    price_paid = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True, #TDD için False yerine True alındı (Double booking'de test patlıyor)
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'fitness_class'],
                name='unique_member_class_reservation'
            )
        ]

    def clean(self):
        current_count = Reservation.objects.filter(
            fitness_class=self.fitness_class
        ).exclude(pk=self.pk).count()

        if current_count >= self.fitness_class.capacity:
            raise ValidationError("Class is full")

    def save(self, *args, **kwargs):
        if self.price_paid is None:
            # Mevcut rezervasyon sayısını al (kendisini hariç tut)
            booked = self.fitness_class.reservations.exclude(pk=self.pk).count()
            total = self.fitness_class.capacity
            occupancy_rate = Decimal(booked) / Decimal(total) if total > 0 else Decimal('0')

            # Doğru PricingEngine'i kullan
            self.price_paid = PricingEngine.calculate_class_price(
                base_price=self.fitness_class.base_price,
                membership_type=self.member.membership_type,
                class_datetime=self.fitness_class.date_time,
                current_occupancy_rate=occupancy_rate
            )

        self.clean()
        super().save(*args, **kwargs)
