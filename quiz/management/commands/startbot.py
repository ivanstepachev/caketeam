from django.core.management.base import BaseCommand
import logging

import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

from bot_token import token


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
        PORT = int(os.environ.get('PORT', '5000'))
        bot = telegram.Bot(token=token)
        bot.setWebhook("https://caketeam.herokuapp.com/" + token)

        bot.sendMessage()

        updater = Updater(token)
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=token,
                              webhook_url="https://caketeam.herokuapp.com/" + token)
        updater.idle()