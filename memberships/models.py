from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

User = get_user_model()

class Member(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # services.py ile uyumlu üyelik tipleri
    MEMBERSHIP_CHOICES = [
        ('student', 'Student'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Boy (cm)")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Kilo (kg)")
    
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='standard',
        help_text="Üyelik tipi fiyatlandırma motorunu etkiler."
    )

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - {self.get_membership_type_display()}"

# --- SİNYALLER ---
@receiver(post_save, sender=User)
def create_member_profile(sender, instance, created, **kwargs):
    if created:
        Member.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_member_profile(sender, instance, **kwargs):
    if hasattr(instance, 'member_profile'):
        instance.member_profile.save()

# DİKKAT: Reservation modeli buradan TAMAMEN silindi.