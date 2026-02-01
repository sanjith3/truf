from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key=','):
    """
    Returns the value turned into a list.
    """
    if value:
        return [v.strip() for v in value.split(key) if v.strip()]
    return []
