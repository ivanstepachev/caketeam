import requests
from quiz.models import Token, Staff
import json


# Отправка сообщений через бота
def send_message(chat_id, text, reply_markup=None, **kwargs):
    method = "sendMessage"
    token = Token.objects.get(id=1).token
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
    requests.post(url, data=data)


def handler(chat_id, text):
    if text == '/start':
        if len(Staff.objects.filter(telegram_id=chat_id)) == 0:
            answer = '''Добро пожаловать на платформу. Здесь ты можешь получать кондитерские задание. Для начала нужно пройти регистрацию'''
            keyboard = json.dumps({"inline_keyboard": [[{"text": "Link", 'url': 'https://naira-arina.ru'}]]})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = '''Главное меню'''
            keyboard = json.dumps({'keyboard': [["Заказы"], ["Разместить свободную коробку"]], 'one_time_keyboard': True, 'resize_keyboard': True})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
    else:
        send_message(chat_id=chat_id, text=text)




        # json.dumps({"inline_keyboard": [[{"text": "Link", 'url': 'https://naira-arina.ru'}]]})
        # reply_markup = json.dumps({'keyboard': [["A button"], ["B button"]],
        #                     'one_time_keyboard': True,
        #                     'resize_keyboard': True})