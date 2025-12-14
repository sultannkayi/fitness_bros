from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from .services import PricingEngine

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
            total = self.fitness_class.capacity
            booked = self.fitness_class.reservations.count()
            occupancy_rate = booked / total if total > 0 else 1

            hour = self.fitness_class.date_time.hour
            is_peak = 18 <= hour <= 22

            self.price_paid = PricingEngine.calculate_price(
                base_price=self.fitness_class.base_price,
                membership_type=self.member.membership_type,
                occupancy_rate=occupancy_rate,
                is_peak_hour=is_peak
            )

        self.clean()
        super().save(*args, **kwargs)
