# courses/templatetags/courses_extras.py
from django import template

register = template.Library()

@register.filter
def lower_class_name(obj):
    """
    Returns the lowercase class name of an object.
    Useful for dynamic URLs with content types.
    """
    if obj:
        return obj.__class__.__name__.lower()
    return ''


@register.filter
def model_name(obj):
    return obj._meta.model_name.lower()