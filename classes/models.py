from django.db import models


class FitnessClass(models.Model):
    """Model representing a fitness class offered at the gym."""
    
    CLASS_TYPES = [
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('spinning', 'Spinning'),
        ('hiit', 'HIIT'),
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('crossfit', 'CrossFit'),
        ('dance', 'Dance'),
    ]
    
    name = models.CharField(max_length=200)
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=100)
    schedule = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    capacity = models.PositiveIntegerField(default=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['schedule']
        verbose_name = 'Fitness Class'
        verbose_name_plural = 'Fitness Classes'
    
    def __str__(self):
        return f"{self.name} - {self.schedule.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def available_spots(self):
        """Return the number of available spots in this class."""
        return self.capacity - self.reservations.filter(status='confirmed').count()
    
    @property
    def is_full(self):
        """Check if the class is at full capacity."""
        return self.available_spots <= 0
