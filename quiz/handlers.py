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


def handler(chat_id, text, username):
    # Обработка /start в зависимости есть ли кондитер в БД
    if text.lower() == '/start':
        if len(Staff.objects.filter(telegram_id=chat_id)) == 0:
            answer = '''Добро пожаловать на платформу. Здесь ты можешь получать кондитерские задание. Для начала нужно пройти регистрацию'''
            keyboard = json.dumps({"inline_keyboard": [[{"text": "Регистрация", 'url': f'https://caketeam.herokuapp.com/reg/{chat_id}/{username.lower()}'}]]})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = '''Главное меню'''
            keyboard = json.dumps({'keyboard': [["Заказы"], ["Мой профиль"], ["Мой pin-код"], ["Тех поддержка"]], 'one_time_keyboard': True, 'resize_keyboard': True})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)

    elif text == 'Заказы' or text == 'заказы':
        if len(Staff.objects.filter(telegram_id=chat_id)) > 0:
            answer = '''Перейдите по ссылке, чтобы посмотреть все последние заказы на десерты'''
            keyboard = json.dumps({"inline_keyboard": [
                [{"text": "Все заказы", 'url': f'https://caketeam.herokuapp.com/a/orders'}]]})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = '''Вы не зарегистрированы. Нажмите /start'''
            send_message(chat_id=chat_id, text=answer)

    elif text == 'Мой профиль' or text == 'мой профиль':
        if len(Staff.objects.filter(telegram_id=chat_id)) > 0:
            answer = '''Перейдите по ссылке, чтобы внести изменения в свой профиль.\n\nЗдесь вы можете добавить себе аватар, написать про свои навыки и поставить фильтр по городам, по которым будут приходить уведомления о новых заказах.'''
            keyboard = json.dumps({"inline_keyboard": [
                [{"text": "Редактировать мой профиль", 'url': f'https://caketeam.herokuapp.com/a/profile/{chat_id}'}]]})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = '''Вы не зарегистрированы. Нажмите /start'''
            send_message(chat_id=chat_id, text=answer)

    elif text == 'Мой pin-код' or text == 'мой pin-код':
        if len(Staff.objects.filter(telegram_id=chat_id)) > 0:
            staff = Staff.objects.filter(telegram_id=chat_id)[0]
            answer = f'''Pin-код нужен, для того чтобы оставить быстрый отклик на задание, если вы не авторизованы на сайте и на авторизацию не хотите тратить время, достаточно при отклике на заказ ввести в поле свой pin-код. Если вы авторизованы pin-код будет автоматически введен в поле. \n\n Ваш pin-код: {staff.pin}'''
            keyboard = json.dumps({'keyboard': [["Заказы"], ["Мой профиль"], ["Мой pin-код"], ["Тех поддержка"]],
                                   'one_time_keyboard': True, 'resize_keyboard': True})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = '''Вы не зарегистрированы. Нажмите /start'''
            send_message(chat_id=chat_id, text=answer)
    elif text == 'Тех поддержка' or text == 'тех поддержка':
        if len(Staff.objects.filter(telegram_id=chat_id)) > 0:
            answer = f'''Контакт тех.поддержки в Telegram: @i1ness'''
            keyboard = json.dumps({'keyboard': [["Заказы"], ["Мой профиль"], ["Мой pin-код"], ["Тех поддержка"]],
                                   'one_time_keyboard': True, 'resize_keyboard': True})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = f'''Контакт тех.поддержки в Telegram: @i1ness'''
            send_message(chat_id=chat_id, text=answer)

    # Любой другой текст переводит в главное меню если кондитер зарегистрирован
    else:
        if len(Staff.objects.filter(telegram_id=chat_id)) > 0:
            answer = '''Главное меню'''
            keyboard = json.dumps(
                {'keyboard': [["Заказы"], ["Мой профиль"], ["Мой pin-код"]], 'one_time_keyboard': True,
                 'resize_keyboard': True})
            send_message(chat_id=chat_id, text=answer, reply_markup=keyboard)
        else:
            answer = '''Вы не зарегистрированы. Нажмите /start'''
            send_message(chat_id=chat_id, text=answer)




        # json.dumps({"inline_keyboard": [[{"text": "Link", 'url': 'https://naira-arina.ru'}]]})
        # reply_markup = json.dumps({'keyboard': [["A button"], ["B button"]],
        #                     'one_time_keyboard': True,
        #                     'resize_keyboard': True})