from quiz.models import OrderCounter, Staff, Review
from service.settings import hashid_salt, alphabet
from hashids import Hashids


# Returns if unique view of order details
def unique_view_of_order(order, staff):
    views = OrderCounter.objects.filter(order=order, staff=staff)
    if len(views) == 0:
        OrderCounter.objects.create(order=order, staff=staff)
        return True
    else:
        return False


# Для генерации секретных ссылок
def to_hash(numb):
    hashids = Hashids(salt=hashid_salt, alphabet=alphabet, min_length=5)
    return hashids.encode(numb)


# Для генерации секретных ссылок
def from_hash(hash_str):
    hashids = Hashids(salt=hashid_salt, alphabet=alphabet, min_length=5)
    return hashids.decode(hash_str)[0]


# Возвразает средний рейтинг кондитера
def mean_rating(staff):
    reviews = Review.objects.filter(staff=staff)
    reviews_amount = len(Review.objects.filter(staff=staff))
    if reviews_amount == 0:
        result = 0
    else:
        sum_reviews = 0
        for review in reviews:
            sum_reviews += review.rating
        result = sum_reviews/reviews_amount
    return result


# Меняет формат даты с квиза
def format_date(date):
    d = date.split('-')
    return f'{d[2]}.{d[1]}.{d[0]}'
