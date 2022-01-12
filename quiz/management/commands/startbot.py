from django.core.management.base import BaseCommand
import telegram
from telegram.ext import Updater
import os

from bot_token import token as t

class Command(BaseCommand):
    help = 'Bot Starting'

    def handle(self, *args, **options):
        """Start the bot."""
        token = t
        PORT = int(os.environ.get('PORT', '5000'))
        bot = telegram.Bot(token=token)
        bot.setWebhook("https://caketeam.herokuapp.com/" + token)
        bot.sendMessage()

        updater = Updater(token)
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=token,
                              webhook_url="https://caketeam.herokuapp.com/" + token)
        updater.idle()

