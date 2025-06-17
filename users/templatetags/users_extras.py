# users/templatetags/users_extras.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to a Django form field's widget.
    Usage: {{ field|add_class:"your-css-class" }}
    """
    return field.as_widget(attrs={"class": css_class})