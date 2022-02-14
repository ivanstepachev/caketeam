from django import template

register = template.Library()


# range для шаблона чтобы делать рейтинг из звездочек
@register.filter
def range_rating(int):
    return range(int)