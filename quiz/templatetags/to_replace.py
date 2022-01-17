from django import template

register = template.Library()

@register.filter
def to_replace(value):
    return value.replace("-", "<br>")