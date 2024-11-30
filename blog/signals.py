from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import *


# Notify author when they are followed
@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.followee,
            sender=instance.follower,
            notification_type='follow'
        )

# Notify author when their post gets a like
@receiver(m2m_changed, sender=Blog.likes.through)
def blog_liked(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            sender_user = instance.likes.get(pk=user_id)
            if instance.author != sender_user:
                Notification.objects.create(
                    recipient=instance.author,
                    sender=sender_user,
                    notification_type='like',
                    blog=instance
                )


# Notify author when their post receives a comment
@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created and instance.blog.author != instance.author:
        Notification.objects.create(
            recipient=instance.blog.author,
            sender=instance.author,
            notification_type='comment',
            blog=instance.blog,
            comment=instance
        )
