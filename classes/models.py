from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class FitnessClass(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    capacity = models. PositiveIntegerField()
    date_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=7, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.capacity <= 0:
            raise ValidationError("Capacity must be positive")

        if self.date_time <= timezone.now():
            raise ValidationError("Class date must be in the future")

    def __str__(self):
        instructor_name = (
            self.instructor.first_name
            if self.instructor.first_name
            else self.instructor.email
        )
        return f"{self.name} - {instructor_name} ({self.date_time. strftime('%Y-%m-%d %H:%M')})"