from django import template
from quiz.models import Respond

register = template.Library()

@register.filter
def count_done_orders(orders):
    counter = 0
    for order in orders:
        if order.status == "DONE":
            counter += 1
    return counter
