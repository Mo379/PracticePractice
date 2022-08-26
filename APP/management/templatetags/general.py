from django import template

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """Splits a string into a list using key"""
    return value.split(key)


@register.filter(name='index')
def index(indexable, i):
    """ Return ith index of list"""
    return indexable[i]


@register.filter(name='list_to_string')
def list_to_string(indexable, key):
    """ Turn the list into a string """
    indexable = list(indexable)
    lista = []
    for i in indexable:
        lista.append(str(i))
    string = str(key).join(lista)
    return string


@register.filter(name='has_group')
def has_group(user, group_name):
    """ The user is in this group"""
    return user.groups.filter(name=group_name).exists()


@register.filter(name='has_many_groups')
def has_many_groups(user, group_list_str):
    """ The user is in all of these groups """
    groups = group_list_str.split(' ')
    reports = []
    for group_name in groups:
        status = user.groups.filter(name=group_name).exists()
        if status:
            reports.append(status)
        else:
            reports.append(status)
    if False in reports:
        return False
    else:
        return True


@register.filter(name='in_groups')
def in_groups(user, group_list_str):
    """ The user is at least in one of these groups"""
    groups = group_list_str.split(' ')
    reports = []
    for group_name in groups:
        status = user.groups.filter(name=group_name).exists()
        if status:
            reports.append(status)
        else:
            reports.append(status)
    if True in reports:
        return True
    else:
        return False


@register.simple_tag
def definevar(val=None):
    """ Define this variable """
    return val




