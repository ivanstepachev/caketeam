from django.shortcuts import render, redirect
from quiz.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

import telegram
import requests

bot = telegram.Bot('5043578506:AAGe4gsEVX9Rhy0ZkdKyb3qRReSgPm6neuA')

def quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        type_of_cake = request.POST.get('type_of_cake')
        message = request.POST.get('message')
        order = Order(name=name, phone=phone, type_of_cake=type_of_cake, message=message)
        order.save()

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
        send_message(chat_id=chat_id, text='blablabla')
    return HttpResponse('ok', content_type='text/plain', status=200)
