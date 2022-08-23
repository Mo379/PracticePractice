from django import template

register = template.Library()


def split(value, key):
    """Splits a string into a list using key"""
    return value.split(key)


def index(indexable, i):
    return indexable[i]


@register.simple_tag
def definevar(val=None):
    return val


register.filter('split', split)
register.filter('index', index)

