from django.shortcuts import render, redirect, get_object_or_404
from quiz.models import Order, Token, Note, Respond, Image, Staff
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

import requests

from quiz.handlers import handler

admin_id = 896205315


def quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        type_of_cake = request.POST.get('type_of_cake')
        message = request.POST.get('message')
        order = Order(name=name, phone=phone, type_of_cake=type_of_cake, message=message)
        order.save()
        order_text = f'''Имя: {order.name}
        Телефон: {order.phone}
        Десерт: {order.type_of_cake}
        Примечание: {order.message}
        https://caketeam.herokuapp.com/orders/{order.id}'''
        admin_staff_list = Staff.objects.filter(admin=True)
        for admin_staff in admin_staff_list:
            send_message(chat_id=int(admin_staff.telegram_id), text=order_text)
        return redirect('quiz')
    else:
        return render(request, 'quiz/index.html')


def orders(request):
    orders = Order.objects.all()
    return render(request, 'quiz/orders.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        text = request.POST.get('note')
        note = Note(text=text, order=order)
        note.save()
        comments = ''
        notes = Note.objects.filter(order=order)
        for note in notes:
            comments += '\n' + str(note.date) + note.text
        order_text = f'''Десерт: {order.type_of_cake}
                Примечание: {order.message}
                Комментарии: {comments}
                https://caketeam.herokuapp.com/{order.id}'''
        staff_list = Staff.objects.all()
        for staff in staff_list:
            send_message(chat_id=int(staff.telegram_id), text=order_text)
        return redirect('order_detail', order_id)
    else:
        notes = Note.objects.filter(order=order)
        responds = Respond.objects.filter(order=order)
        if responds is not None:
            return render(request, 'quiz/order_detail.html', {'order': order, 'notes': notes, 'responds': responds})
        return render(request, 'quiz/order_detail.html', {'order': order, 'notes': notes})


# Оставляем отклик
def order_respond(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        text = request.POST.get('message')
        # Так как несколько изображений
        images = request.FILES.getlist('images')
        respond = Respond.objects.create(text=text, order=order)
        if images:
            for image in images:
                Image.objects.create(image=image, respond=respond)
        return redirect('order_respond', order_id)
    else:
        notes = Note.objects.filter(order=order)
        return render(request, 'quiz/order_respond.html', {'order': order, 'notes': notes})


def send_message(chat_id, text):
    method = "sendMessage"
    token = Token.objects.get(id=1).token
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


@csrf_exempt
def bot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            if 'username' in data["message"]["chat"]:
                handler(chat_id=chat_id, text=text)
            else:
                text = '''Сначала сделайте себе никнейм'''
                send_message(chat_id=chat_id, text=text)
    return HttpResponse('ok', content_type='text/plain', status=200)


def setwebhook(request):
    if request.method == "POST":
        token = request.POST.get('token')
        link = request.POST.get('link')
        token_exist = Token.objects.filter(id=1)
        if token_exist:
            new_token = token_exist[0]
            new_token.token = token
            new_token.save()
        else:
            new_token = Token(id=1, token=token)
            new_token.save()
        requests.get(f'https://api.telegram.org/bot{token}/setWebhook?url=https://{link}/bot')
        return redirect('setwebhook')
    else:
        url = request.build_absolute_uri().split('/')[2]
        return render(request, 'quiz/setwebhook.html', {'url': url})


def deletewebhook(request):
    if request.method == "POST":
        token = request.POST.get('token')
        requests.get(f'https://api.telegram.org/bot{token}/deleteWebhook')
        return redirect('deletewebhook')
    else:
        token = Token.objects.filter(id=1)
        return render(request, 'quiz/deletewebhook.html', {'token': token})


# {'update_id': 541049445, 'message':
#     {'message_id': 60, 'from':
#         {'id': 896205315, 'is_bot': False, 'first_name': 'Ivan', 'username': 'ivan40', 'language_code': 'ru'},
#      'chat': {'id': 896205315, 'first_name': 'Ivan', 'username': 'ivan40', 'type': 'private'},
#      'date': 1641148166, 'text': 'Hdbcnf'}}

# {'update_id': 541049484, 'my_chat_member':
#     {'chat': {'id': 1715664500, 'first_name': 'Alina', 'type': 'private'},
#      'from': {'id': 1715664500, 'is_bot': False, 'first_name': 'Alina', 'language_code': 'ru'},
#      'date': 1642118668, 'old_chat_member': {'user': {'id': 5043578506, 'is_bot': True, 'first_name': 'FirstBot', 'username': 'i1nes_bot'},
#             'status': 'member'}, 'new_chat_member': {'user': {'id': 5043578506, 'is_bot': True, 'first_name': 'FirstBot', 'username': 'i1nes_bot'}, 'status': 'kicked', 'until_date': 0}}}