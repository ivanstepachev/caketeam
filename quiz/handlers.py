import requests
from quiz.models import Token, Staff


# Отправка сообщений через бота
def send_message(chat_id, text, reply_markup=None, **kwargs):
    method = "sendMessage"
    token = Token.objects.get(id=1).token
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


def handler(chat_id, text):
    if text == '/start':
        answer = '''Добро пожаловать на платформу. Здесь ты можешь получать кондитерские задание. Нажми начать для старта'''
        send_message(chat_id=chat_id, text=answer, reply_markup={"inline_keyboard":[[{"text":"yes","callback_data":"yes"}]]})
    else:
        send_message(chat_id=chat_id, text=text)