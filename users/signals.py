from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from users.models import Profile
from django.utils.text import slugify

@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    """
    Create a user profile when a new user is created or save the profile on user updates.
    """
    # Create the profile only if the user is newly created
    if created:
        Profile.objects.create(user=instance)
        print(f"Profile created for {instance.username}")
    else:
        # Save the profile if the user is updated
        instance.profile.save()
        print(f"Profile saved for {instance.username}")



@receiver(user_signed_up)
def populate_user_profile(request, user, **kwargs):
    """
    Signal to populate Profile and ensure `username` is generated for Google OAuth users.
    """
    social_login = kwargs.get('sociallogin', None)
    if social_login and social_login.account.provider == 'google':
        user_data = social_login.account.extra_data
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name

        # Generate a unique username if not provided
        if not user.username:
            base_username = slugify(user_data.get('name', user.email.split('@')[0]))
            username = base_username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username

        user.save()

        # Update or create the Profile
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            },
        )
