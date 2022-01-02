from django.shortcuts import render, redirect
from quiz.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

import requests


def quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        type_of_cake = request.POST.get('type_of_cake')
        message = request.POST.get('message')
        order = Order(name=name, phone=phone, type_of_cake=type_of_cake, message=message)
        order.save()
        order_text = f'''
        Имя: {order.name}
        Телефон: {order.phone}
        Десерт: {order.type_of_cake}
        Примечание: {order.message}'''
        send_message(chat_id=896205315, text=order_text)
        return redirect('quiz')
    else:
        return render(request, 'quiz/index.html')


def orders(request):
    orders = Order.objects.all()
    return render(request, 'quiz/orders.html', {'orders': orders})


def send_message(chat_id, text):
    method = "sendMessage"
    token = "5043578506:AAGe4gsEVX9Rhy0ZkdKyb3qRReSgPm6neuA"
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


@csrf_exempt
def bot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        send_message(chat_id=chat_id, text=text)
    return HttpResponse('ok', content_type='text/plain', status=200)

# {'update_id': 541049445, 'message':
#     {'message_id': 60, 'from':
#         {'id': 896205315, 'is_bot': False, 'first_name': 'Ivan', 'username': 'ivan40', 'language_code': 'ru'},
#      'chat': {'id': 896205315, 'first_name': 'Ivan', 'username': 'ivan40', 'type': 'private'},
#      'date': 1641148166, 'text': 'Hdbcnf'}}