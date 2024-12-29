# blog/context_processors.py

from .models import Notification

def notifications(request):
    """
    Context processor to pass notifications to the template globally.
    """
    if request.user.is_authenticated:
        # Fetch notifications for the logged-in user
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

        # Fetch unread notifications count
        unread_notifications_count = notifications.filter(is_read=False).count()

        return {
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        }
    return {}
