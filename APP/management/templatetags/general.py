from django import template

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """Splits a string into a list using key"""
    return value.split(key)


@register.filter(name='index')
def index(indexable, i):
    return indexable[i]


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.simple_tag
def definevar(val=None):
    return val




