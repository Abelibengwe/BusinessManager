#!/usr/bin/env python
"""
Script to create test notifications for debugging
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BusinessManager.settings')
django.setup()

from django.contrib.auth.models import User
from BusinessApp.models import Notification, Product

def create_test_notifications():
    """Create some test notifications"""
    try:
        # Get the first user (usually admin)
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return
        
        print(f"Creating test notifications for user: {user.username}")
        
        # Create some test notifications
        notifications_data = [
            {
                'title': 'Low Stock Alert: Test Product 1',
                'message': 'Test Product 1 is running low on stock. Only 3 units remaining.',
                'notification_type': 'warning'
            },
            {
                'title': 'Maintenance Due: Test Equipment',
                'message': 'Test Equipment requires maintenance. Due date: Today',
                'notification_type': 'warning'
            },
            {
                'title': 'Critical Alert: System Check',
                'message': 'System requires immediate attention.',
                'notification_type': 'error'
            },
            {
                'title': 'Project Deadline: Test Project',
                'message': 'Test Project deadline is approaching in 3 days.',
                'notification_type': 'info'
            },
            {
                'title': 'High Expense Alert',
                'message': 'Large expense recorded: $1500 for office supplies.',
                'notification_type': 'warning'
            }
        ]
        
        # Delete existing test notifications to avoid duplicates
        Notification.objects.filter(
            user=user,
            title__startswith='Test'
        ).delete()
        
        # Create new test notifications
        created_count = 0
        for notif_data in notifications_data:
            notification = Notification.objects.create(
                user=user,
                **notif_data
            )
            created_count += 1
            print(f"Created notification: {notification.title}")
        
        # Count total unread notifications
        total_unread = Notification.objects.filter(user=user, is_read=False).count()
        print(f"\nTotal unread notifications for {user.username}: {total_unread}")
        print(f"Created {created_count} test notifications.")
        
        # Also check if there are any products that should trigger low stock alerts
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=10,  # Assuming min_stock_level is usually around 10
            is_active=True
        )
        
        print(f"\nFound {low_stock_products.count()} low stock products:")
        for product in low_stock_products[:5]:  # Show first 5
            print(f"- {product.name}: {product.stock_quantity} units (min: {product.min_stock_level})")
        
    except Exception as e:
        print(f"Error creating test notifications: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_notifications()
