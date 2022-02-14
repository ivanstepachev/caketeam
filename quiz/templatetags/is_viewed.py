from django import template
from quiz.models import OrderCounter

register = template.Library()


# проверка, если страница просмотрена
@register.filter
def is_viewed(order, staff):
    return len(OrderCounter.objects.filter(order=order, staff=staff)) > 0
