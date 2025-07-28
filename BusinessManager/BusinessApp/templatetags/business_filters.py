from django import template
from django.utils.safestring import mark_safe
import math

register = template.Library()

@register.filter
def abs_value(value):
    """Return the absolute value of a number"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """Format a number as full currency with commas"""
    try:
        return f"TSh {float(value):,.2f}"
    except (ValueError, TypeError):
        return "TSh 0.00"

@register.filter
def currency_full(value):
    """Format a number as full currency with commas"""
    try:
        return f"TSh {float(value):,.2f}"
    except (ValueError, TypeError):
        return "TSh 0.00"

@register.filter
def currency_no_decimal(value):
    """Format a number as currency without decimal places"""
    try:
        return f"TSh {float(value):,.0f}"
    except (ValueError, TypeError):
        return "TSh 0"

@register.filter
def percentage(value):
    """Format a number as percentage"""
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

@register.filter
def status_badge(status):
    """Return Bootstrap badge class for status"""
    status_classes = {
        'working': 'badge-success',
        'maintenance': 'badge-warning',
        'repair': 'badge-danger',
        'damaged': 'badge-danger',
        'retired': 'badge-secondary',
        'outstanding': 'badge-warning',
        'partial': 'badge-info',
        'paid': 'badge-success',
        'overdue': 'badge-danger',
        'active': 'badge-success',
        'inactive': 'badge-secondary',
    }
    return status_classes.get(status.lower(), 'badge-primary')

@register.filter
def truncate_words_html(value, arg):
    """Truncate text and add HTML ellipsis"""
    try:
        words = value.split()
        if len(words) > int(arg):
            truncated = ' '.join(words[:int(arg)])
            return mark_safe(f"{truncated}...")
        return value
    except (ValueError, TypeError, AttributeError):
        return value

@register.filter
def format_number(value):
    """Format a number with thousand separators"""
    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return "0"

@register.filter 
def multiply(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
