from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

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
