from django.shortcuts import render, redirect, get_object_or_404
from quiz.models import Order, Token, Respond, Image, Staff
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

import requests

from quiz.handlers import handler, send_message

from service.settings import admin_id


def quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        type_of_cake = request.POST.get('type_of_cake')
        message = request.POST.get('message')
        order = Order(name=name, phone=phone, type_of_cake=type_of_cake, message=message, status="NEW", note="")
        order.save()
        order_text = f'''Имя: {order.name}\nТелефон: {order.phone}\nДесерт: {order.type_of_cake}\nПримечание: {order.message}'''
        keyboard = json.dumps({"inline_keyboard": [[{"text": "Разместить задание", 'url': f'https://caketeam.herokuapp.com/orders/{order.id}'}]]})
        admin_staff_list = Staff.objects.filter(admin=True)
        for admin_staff in admin_staff_list:
            send_message(chat_id=int(admin_staff.telegram_id), text=order_text, reply_markup=keyboard)
        return redirect('quiz')
    else:
        return render(request, 'quiz/index.html')


def registration(request, chat_id, username):
    if request.method == 'POST':
        city = request.POST.get('city').capitalize()
        name = request.POST.get('name').capitalize()
        surname = request.POST.get('surname').capitalize()
        phone = request.POST.get('phone')
        instagram = request.POST.get('instagram').lower()
        pin = chat_id[-4:]
        staff = Staff(username=username.lower(),
                      telegram_id=chat_id,
                      city=city,
                      name=name,
                      surname=surname,
                      pin=pin,
                      phone=phone,
                      instagram=instagram)
        staff.save()
        # Добавить клавиатуру для добавления пользователя
        send_message(chat_id=admin_id, text=f'''Новый пользователь зарегистрировался @{username.lower()}''')
        return redirect('quiz')
    if request.method == 'GET':
        pin = chat_id[-4:]
        return render(request, 'quiz/registration.html', {'pin': pin, 'username': username})


def staff_list(request):
    active = Staff.objects.filter(active=True).order_by('-date')
    inactive = Staff.objects.filter(active=False).order_by('-date')
    return render(request, 'quiz/staff_list.html', {'active': active, 'inactive': inactive})


def staff_activate(request, chat_id):
    staff = Staff.objects.filter(telegram_id=chat_id)[0]
    staff.active = True
    staff.save()
    return redirect('staff_list')


def staff_deactivate(request, chat_id):
    staff = Staff.objects.filter(telegram_id=chat_id)[0]
    staff.active = False
    staff.save()
    return redirect('staff_list')


def staff_delete(request, chat_id):
    staff = Staff.objects.filter(telegram_id=chat_id)[0]
    staff.delete()
    return redirect('staff_list')


def orders(request):
    if request.GET.get("status") == "ALL":
        orders = Order.objects.all().order_by('-date')
    elif request.GET.get("status") == "NEW":
        orders = Order.objects.filter(status="NEW").order_by('-date')
    elif request.GET.get("status") == "FIND":
        orders = Order.objects.filter(status="FIND").order_by('-date')
    elif request.GET.get("status") == "WORK":
        orders = Order.objects.filter(status="WORK").order_by('-date')
    elif request.GET.get("status") == "DONE":
        orders = Order.objects.filter(status="DONE").order_by('-date')
    else:
        orders = Order.objects.all().order_by('-date')
    return render(request, 'quiz/orders.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        max_responds = request.POST.get('max_responds')
        order.max_responds = max_responds
        order.status = "FIND"
        order.note = note
        order.save()
        # Внутренний код заявки в виде хэштега
        numb_of_order = order.set_numb_of_order()
        staff_list = Staff.objects.filter(active=True)
        print(staff_list)
        for staff in staff_list:
            order_text = f'''Заявка {numb_of_order}\n{order.note}'''
            keyboard = json.dumps({"inline_keyboard": [[{"text": "Оставить заявку", 'url': f'https://caketeam.herokuapp.com/{order.id}/{staff.telegram_id}'}]]})
            send_message(chat_id=int(staff.telegram_id), text=order_text, reply_markup=keyboard)
        return redirect('orders')
    else:
        notes = order.note
        responds = Respond.objects.filter(order=order)
        # Если заметка еще не была создана, вставляем шаблон, если была то редактируем
        if notes == "":
            value =f'''- Десерт: {order.type_of_cake}\n- Город:\n- Дата и время:\n- Доставка/Самовывоз:\n- Примечание:'''
        else:
            value = notes
        # Если есть отклики
        if responds is not None:
            return render(request, 'quiz/order_detail.html', {'order': order, 'notes': notes, 'value': value, 'responds': responds})
        return render(request, 'quiz/order_detail.html', {'order': order, 'value': value, 'notes': notes})


# Оставляем отклик
def order_respond(request, order_id, telegram_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        text = request.POST.get('message')
        pin = request.POST.get('pin')
        num = request.POST.get('num')
        staff = Staff.objects.filter(id=num)
        # Так как несколько изображений
        images = request.FILES.getlist('images')
        if str(staff[0].pin) == str(pin):
            # Нужно привязать к юзеру
            respond = Respond.objects.create(text=text, order=order, staff=staff[0])
            if images:
                for image in images:
                    Image.objects.create(image=image, respond=respond)
            return redirect('quiz')
        else:
            return redirect('quiz')   # Тут надо вызвать ошибку
    elif request.method == 'GET':
        notes = order.note
        telegram_id = telegram_id
        staff = Staff.objects.filter(telegram_id=str(telegram_id))
        # Для отображения количества откликов максимальных
        responds = len(Respond.objects.filter(order=order))
        # Для проверки отклика по пину сотрудника через id чтобы не показывать пин на странице в коде
        num = staff[0].id

        # Проверка на оставленный отзыв данным юзером
        respond = Respond.objects.filter(order=order, staff=staff[0])
        no_respond = len(respond) == 0

        context = {'order': order, 'notes': notes, 'num': num, 'responds': responds, 'no_respond': no_respond}
        return render(request, 'quiz/order_respond.html', context)


# Список заявок каждого кондитера
def responds_list(request, chat_id):
    staff = Staff.objects.filter(telegram_id=chat_id)[0]
    responds = Respond.objects.filter(staff=staff).order_by('-date')
    return render(request, 'quiz/responds.html', {'responds': responds})


@csrf_exempt
def bot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            if 'username' in data["message"]["chat"]:
                username = data["message"]["chat"]["username"]
                handler(chat_id=chat_id, text=text, username=username)
            else:
                text = '''Сначала сделайте себе ник нейм'''
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