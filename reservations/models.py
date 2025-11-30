from django.db import models
from django.core.exceptions import ValidationError


class Reservation(models.Model):
    """Model representing a reservation for a fitness class."""
    
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlist', 'Waitlist'),
    ]
    
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
    reserved_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-reserved_at']
        unique_together = ['member', 'fitness_class']
    
    def __str__(self):
        return f"{self.member} - {self.fitness_class.name}"
    
    def clean(self):
        """Validate the reservation before saving."""
        if self.status == 'confirmed':
            self._validate_capacity()
            self._validate_member_active()
    
    def _validate_capacity(self):
        """Check if there's available capacity in the fitness class."""
        if self.pk:
            # If updating existing reservation, exclude current reservation from count
            confirmed_count = self.fitness_class.reservations.filter(
                status='confirmed'
            ).exclude(pk=self.pk).count()
        else:
            confirmed_count = self.fitness_class.reservations.filter(
                status='confirmed'
            ).count()
        
        if confirmed_count >= self.fitness_class.capacity:
            raise ValidationError(
                {'fitness_class': 'This fitness class is at full capacity.'}
            )
    
    def _validate_member_active(self):
        """Ensure the member has an active membership."""
        if not self.member.is_active:
            raise ValidationError(
                {'member': 'Cannot make reservation for inactive member.'}
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
