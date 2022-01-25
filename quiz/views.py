from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from quiz.models import Order, Token, Respond, Image, Staff
from django.contrib.auth import login, authenticate
from quiz.forms import RegisterForm
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
        respond_price = request.POST.get('budget')
        message = request.POST.get('message')
        order = Order(name=name, phone=phone, type_of_cake=type_of_cake, message=message, status="NEW", note="", respond_price=int(respond_price))
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
        username = username.lower()
        name = request.POST.get('name').capitalize()
        surname = request.POST.get('surname').capitalize()
        phone = request.POST.get('phone')
        city = request.POST.get('city').capitalize()
        instagram = request.POST.get('instagram').lower()
        pin = chat_id[-4:]
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            staff = Staff(username=username, telegram_id=chat_id, city=city, name=name, surname=surname, pin=pin, phone=phone, instagram=instagram, user=user)
            staff.save()
        # Добавить клавиатуру для добавления пользователя
        send_message(chat_id=admin_id, text=f'''Новый пользователь зарегистрировался @{username.lower()}''')
        return redirect('quiz')
    if request.method == 'GET':
        user_form = RegisterForm()
        pin = chat_id[-4:]
        return render(request, 'quiz/registration.html', {'pin': pin, 'username': username.lower(), 'form': user_form})


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
        respond_price = request.POST.get('respond_price')
        order.max_responds = max_responds
        order.respond_price = int(respond_price)
        order.status = "FIND"
        order.note = note
        order.save()
        # Внутренний код заявки в виде хэштега
        numb_of_order = order.set_numb_of_order()
        staff_list = Staff.objects.filter(active=True)
        for staff in staff_list:
            order_text = f'''Заявка {numb_of_order}\n{order.note.replace(";", "")}'''
            keyboard = json.dumps({"inline_keyboard": [[{"text": "Оставить заявку", 'url': f'https://caketeam.herokuapp.com/{order.id}/{staff.telegram_id}'}]]})
            send_message(chat_id=int(staff.telegram_id), text=order_text, reply_markup=keyboard)
        return redirect('orders')
    else:
        notes = order.note
        responds = Respond.objects.filter(order=order)
        respond_price = order.respond_price
        # Для указания бюджета
        budget = ''
        if respond_price == 50:
            budget = 'До 1500 руб'
        elif respond_price == 100:
            budget = '1500 - 3000 руб'
        else:
            budget = 'Больше 3000 руб'
        # Если заметка еще не была создана, вставляем шаблон, если была то редактируем
        if notes == "":
            value =f'''Имя: {order.name};\nДесерт: {order.type_of_cake};\nГород: ;\nДата и время: ;\nДоставка/Самовывоз: ;\nБюджет: {budget};\nПримечание: ;'''
        else:
            value = notes
        # Если есть отклики
        if responds is not None:
            # Если уже выбран исполнитель
            if order.staff is not None:
                staff = order.staff
                respond = Respond.objects.filter(order=order, staff=staff)[0]
                return render(request, 'quiz/order_detail.html',
                              {'order': order, 'notes': notes, 'value': value, 'respond_price': respond_price, 'respond': respond})
            return render(request, 'quiz/order_detail.html', {'order': order, 'notes': notes, 'value': value, 'respond_price': respond_price, 'responds': responds})

        # Если нет откликов
        return render(request, 'quiz/order_detail.html', {'order': order, 'value': value, 'respond_price': respond_price, 'notes': notes})


# Оставляем отклик
def order_respond(request, order_id, telegram_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        text = request.POST.get('message')
        price = request.POST.get('price')
        pin = request.POST.get('pin')
        staff = Staff.objects.filter(telegram_id=telegram_id)
        # Так как несколько изображений
        images = request.FILES.getlist('images')
        if str(staff[0].pin) == str(pin):
            # Проверка на оставленный отзыв, если его нет, значит это первичное размещение отзыва и деньги списываются, а редактирование бесплатно
            if len(Respond.objects.filter(order=order, staff=staff[0])) == 0:
                # Нужно привязать к юзеру
                respond = Respond.objects.create(text=text, order=order, staff=staff[0], price=price)
                if images:
                    for image in images:
                        Image.objects.create(image=image, respond=respond)
                staff = staff[0]
                staff.balance = staff.balance - order.respond_price
                staff.save()
            # Редактирование уже оставленный отзыв
            else:
                respond = Respond.objects.filter(order=order, staff=staff[0])[0]
                respond.text = text
                respond.price = price
                respond.save()
                if images:
                    for image in images:
                        Image.objects.create(image=image, respond=respond)
            return redirect('quiz')
        else:
            return redirect('quiz')   # Тут надо вызвать ошибку неправильного пина
    elif request.method == 'GET':
        notes = order.note.replace('-', '<br>')
        telegram_id = telegram_id
        staff = Staff.objects.filter(telegram_id=str(telegram_id))
        # Для отображения количества откликов максимальных
        amount_responds = len(Respond.objects.filter(order=order))
        # Для проверки отклика по пину сотрудника через id чтобы не показывать пин на странице в коде
        num = staff[0].id

        # Проверка на оставленный отзыв данным юзером
        if len(Respond.objects.filter(order=order, staff=staff[0])) > 0:
            respond = Respond.objects.filter(order=order, staff=staff[0])[0]
        else:
            respond = None

        # Проверка достаточности баланса
        has_balance = staff[0].balance - order.respond_price >= 0

        context = {'order': order, 'staff': staff[0], 'notes': notes, 'num': num, 'amount_responds': amount_responds, 'respond': respond, 'has_balance': has_balance}
        return render(request, 'quiz/order_respond.html', context)


def respond_choice(request, respond_id):
    respond = get_object_or_404(Respond, id=respond_id)
    staff = respond.staff
    order = respond.order
    order.staff = staff
    order.status = "WORK"
    order.save()
    return redirect('order_detail', order.id)


def respond_delete(request, respond_id):
    respond = get_object_or_404(Respond, id=respond_id)
    order = respond.order
    order.staff = None
    order.status = "FIND"
    order.save()
    return redirect('order_detail', order.id)


def order_done(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "DONE"
    order.save()
    return redirect('order_detail', order.id)


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


def calc(request):
    if request.method == "POST":
        price = request.POST.get('price')
        print(price)
        return redirect('calc')
    else:
        return render(request, 'quiz/calc.html')


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