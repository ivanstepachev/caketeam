from django import template
from quiz.models import Respond

register = template.Library()

@register.filter
def is_responded(order, staff):
    return len(Respond.objects.filter(order=order, staff=staff)) > 0
