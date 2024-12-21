from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Follow, Notification, Blog, Comment, Reaction

# Notify the followee when they are followed
@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    """
    Create a notification for the followee when they are followed.
    """
    if created:
        Notification.objects.create(
            recipient=instance.followee,
            sender=instance.follower,
            notification_type='follow'
        )


# Notify the blog author when their blog receives a comment
@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    """
    Create a notification for the blog author when a comment is added to their blog.
    Exclude notifications if the author comments on their own blog.
    """
    if created and instance.blog.author != instance.author:
        Notification.objects.create(
            recipient=instance.blog.author,
            sender=instance.author,
            notification_type='comment',
            blog=instance.blog,
            comment=instance
        )


# Notify the blog author when their blog receives a reaction
@receiver(post_save, sender=Reaction)
def reaction_created(sender, instance, created, **kwargs):
    """
    Create a notification for the blog author when their blog receives a reaction.
    Exclude notifications if the author reacts to their own blog.
    """
    if created and instance.blog.author != instance.user:
        Notification.objects.create(
            recipient=instance.blog.author,
            sender=instance.user,
            notification_type='reaction',
            blog=instance.blog,
            reaction=instance
        )
