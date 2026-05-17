from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    if hasattr(d, 'get'):
        return d.get(key, [])
    return []
