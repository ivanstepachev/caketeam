from django import template
from quiz.models import Review

register = template.Library()


# range для шаблона чтобы делать рейтинг из звездочек
@register.filter
def mean_rating(respond):
    reviews = Review.objects.filter(staff=respond.staff)
    reviews_amount = len(Review.objects.filter(staff=respond.staff))
    sum_reviews = 0
    for review in reviews:
        sum_reviews += review.rating
    return sum_reviews / reviews_amount