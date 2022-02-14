from django import template
from quiz.models import Respond

register = template.Library()

@register.filter
def won_respond(order, staff):
    respond = Respond.objects.filter(order=order, staff=staff)[0]
    return respond
