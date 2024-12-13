import urllib.parse

from django import template

register = template.Library()

@register.filter
def urlparse_path(value):
    return urllib.parse.urlparse(value).path


@register.filter
def split_path(value):
    return value.split('/')


@register.filter
def startswith(value, arg):
    return value.startswith(arg)

@register.filter
def isdigit(value):
    return value.isdigit()

@register.filter
def group_by(lst, key):
    result = {}
    for item in lst:
        k = getattr(item[0], key)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result.items()