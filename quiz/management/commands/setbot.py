from django.core.management.base import BaseCommand

import requests

from quiz.models import Token


class Command(BaseCommand):
    help = 'Add token and Set Webhook'

    def add_arguments(self, parser):
        parser.add_argument("token", type=str)

    def handle(self, *args, **options):
        token = options["token"]
        token_exist = Token.objects.filter(id=1)
        if token_exist:
            new_token = token_exist[0]
            new_token.token = token
            new_token.save()
        else:
            new_token = Token(id=1, token=token)
            new_token.save()
        requests.get(f'https://api.telegram.org/bot{token}/setWebhook?url=https://caketeam.herokuapp.com/bot')


