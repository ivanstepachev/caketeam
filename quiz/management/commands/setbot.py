from django.core.management.base import BaseCommand

import requests


class Command(BaseCommand):
    help = 'Add token adn SetWebhook'

    def add_arguments(self, parser):
        parser.add_argument("token", type=str)

    def handle(self, *args, **options):
        token = options["token"]
        requests.get(f'https://api.telegram.org/bot{token}/setWebhook?url=https://caketeam.herokuapp.com/{token}')
        file_name = 'bot_token.py'
        with open(file_name, 'w') as f:
            f.write('token = \'{}\''.format(token))