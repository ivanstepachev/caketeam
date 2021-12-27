from django.core.management.base import BaseCommand
import logging

import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

# Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )
#
# logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


class Command(BaseCommand):
    help = 'Bot Starting'

    def handle(self, *args, **options):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # updater = Updater("5043578506:AAGe4gsEVX9Rhy0ZkdKyb3qRReSgPm6neuA")

        token = "5043578506:AAGe4gsEVX9Rhy0ZkdKyb3qRReSgPm6neuA"
        PORT = int(os.environ.get('PORT', '5000'))
        bot = telegram.Bot(token=token)
        bot.setWebhook("https://caketeam.herokuapp.com/" + token)

        updater = Updater(token)
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN,
                              webhook_url="https://caketeam.herokuapp.com/" + token)
        updater.idle()

