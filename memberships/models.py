from django.db import models
from django.conf import settings

class Member(models.Model):

    MEMBERSHIP_CHOICES = [
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
        ('STUDENT', 'Student'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member',
        unique=True  # duplicate prevention
    )

    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='STANDARD'
    )

    is_active_member = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.membership_type}"
