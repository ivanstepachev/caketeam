from django.core.management.base import BaseCommand

import requests

from quiz.models import Order


class Command(BaseCommand):
    help = 'Add token and Set Webhook'


    def handle(self, *args, **options):
        orders = Order.objects.get(id=4)
        orders.delete()
