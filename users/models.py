from django.db import models
from django.utils.timezone import now
from django.core.validators import RegexValidator
from blog.models import Blog
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import random
import time
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    # subscription_type = models.CharField(
    #     max_length=10,
    #     choices=[('monthly', 'Monthly'), ('annual', 'Annual')],
    #     blank=True,
    #     null=True
    # )
    # subscription_end = models.DateTimeField(blank=True, null=True)

    # def is_subscription_active(self):
    #     return self.subscription_end and self.subscription_end > now()



class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='activity')
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_activity_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "UserActivity"
        verbose_name_plural = "UserActivities"

    def __str__(self):
        return f"Activity for {self.user.username}"

class UserBlogInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_interactions')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='user_interactions')
    is_favorite = models.BooleanField(default=False)
    liked = models.BooleanField(default=False, help_text="Indicates if the user liked the blog.")
    commented = models.BooleanField(default=False, help_text="Indicates if the user commented on the blog.")
    last_interaction = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} interaction with {self.blog.title}"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    email_notifications = models.BooleanField(default=True, help_text="Enable or disable email notifications.")
    dark_mode = models.BooleanField(default=False, help_text="Enable or disable dark mode for the app.")

    class Meta:
        verbose_name = "UserSetting"
        verbose_name_plural = "UserSettings"

    def __str__(self):
        return f"Settings for {self.user.username}"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    #expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field to track OTP generation time

    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at


# class OTP(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)

#     def generate_otp(self):
#         """Generate a 6-digit OTP"""
#         self.otp = str(random.randint(100000, 999999))
#         self.created_at = timezone.now()
#         self.is_verified = False
#         self.save()

#     def is_expired(self):
#         """Check if the OTP has expired (set to 5 minutes for this example)"""
#         expiration_time = self.created_at + timedelta(minutes=5)
#         return timezone.now() > expiration_time

#     def __str__(self):
#         return f"OTP for {self.user.username}"

class SubscriptionList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    user_email = models.EmailField(max_length=254)
    time_submitted = models.DateTimeField(default=now)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "SubscriptionList"
        verbose_name_plural = "SubscriptionLists"

    def __str__(self):
        return self.user_email