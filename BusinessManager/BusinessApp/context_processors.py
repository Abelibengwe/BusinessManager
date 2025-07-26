from .models import Notification
import logging

logger = logging.getLogger(__name__)

def notifications(request):
    """
    Context processor to add unread notifications to all templates
    """
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).order_by('-created_at')[:10]
        
        count = unread_notifications.count()
        
        # Debug logging
        logger.debug(f"User {request.user.username} has {count} unread notifications")
        
        return {
            'notifications': unread_notifications,
            'notification_count': count,
        }
    return {
        'notifications': [],
        'notification_count': 0,
    }
