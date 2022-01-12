from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Add token to Database'

    def add_arguments(self, parser):
        parser.add_argument("token", type=str)

    def handle(self, *args, **options):
        token = options["token"]
        file_name = 'bot_token.py'
        with open(file_name, 'w') as f:
            f.write('token = \'{}\''.format(token))
