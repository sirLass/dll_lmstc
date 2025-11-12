# Make sure you have this custom filter defined in your templatetags
from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def lookup(obj, attr):
    """Lookup attribute from object using dot notation"""
    try:
        attrs = attr.split('.')
        result = obj
        for a in attrs:
            if hasattr(result, a):
                result = getattr(result, a)
            elif hasattr(result, '__getitem__'):
                result = result[a]
            else:
                return None
        return result
    except (AttributeError, KeyError, TypeError):
        return None

@register.filter
def to_letter(value):
    """Convert number to letter (1=A, 2=B, etc.)"""
    try:
        num = int(value)
        if 1 <= num <= 26:
            return chr(64 + num)  # 65 is ASCII for 'A'
        return str(value)
    except (ValueError, TypeError):
        return str(value)

@register.filter
def tojson(value):
    """Convert Python object to JSON string"""
    try:
        return json.dumps(value)
    except (ValueError, TypeError):
        return '{}'
