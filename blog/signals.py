from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Follow, Notification, Blog, Comment

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


# Notify the blog author when their post gets liked
@receiver(m2m_changed, sender=Blog.likes.through)
def blog_liked(sender, instance, action, pk_set, **kwargs):
    """
    Create notifications for the blog author when their blog gets likes.
    Exclude the scenario where the author likes their own blog.
    """
    if action == "post_add":  # Triggered after users are added to the 'likes' many-to-many relationship
        for user_id in pk_set:
            sender_user = instance.likes.get(pk=user_id)
            # Avoid notifying the author if they like their own blog
            if instance.author != sender_user:
                Notification.objects.create(
                    recipient=instance.author,
                    sender=sender_user,
                    notification_type='like',
                    blog=instance
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




