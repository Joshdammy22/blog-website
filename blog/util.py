from .models import Notification
from django.utils.timezone import now

def create_reaction_notification(sender, recipient, blog):
    """
    Creates a notification when a user reacts to a blog post.
    """
    if sender != recipient:  # Prevent self-notifications
        Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type='reaction',
            blog=blog,
            created_at=now()
        )


def create_comment_notification(sender, recipient, comment):
    """
    Creates a notification when a user comments on a blog post.
    """
    if sender != recipient:  # Prevent self-notifications
        Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type='comment',
            comment=comment,
            blog=comment.blog,
            created_at=now()
        )


def create_follow_notification(sender, recipient):
    """
    Creates a notification when a user follows another user.
    """
    if sender != recipient:  # Prevent self-notifications
        Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type='follow',
            created_at=now()
        )


def delete_follow_notification(sender, recipient):
    """
    Deletes a notification when a user unfollows another user.
    """
    Notification.objects.filter(
        recipient=recipient,
        sender=sender,
        notification_type='follow'
    ).delete()
