from django.db import models
from django.utils.timezone import now
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
import random
import time
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure email is unique

    USERNAME_FIELD = 'email'  # Allow login using email instead of username
    REQUIRED_FIELDS = ['username']  # Make sure 'username' is required during creation

    def __str__(self):
        return self.email



class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, null=True, help_text="Write a short bio about yourself.")
    email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='authors/', null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        help_text="Enter a valid phone number. Example: +1234567890"
    )
    website = models.URLField(blank=True, null=True, help_text="Add a link to your personal website or portfolio.")
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # To track OTP generation time

    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at


class SubscriptionList(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="subscription")
    user_email = models.EmailField(max_length=254)
    time_submitted = models.DateTimeField(default=now)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "SubscriptionList"
        verbose_name_plural = "SubscriptionLists"

    def __str__(self):
        return self.user_email
