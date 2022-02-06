from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from quiz.models import Order, Token, Respond, Image, Staff, ReferenceImage
from django.contrib.auth import login, authenticate
from quiz.forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404

import json

import requests

from quiz.handlers import handler, send_message
from quiz.utilities import unique_view_of_order, to_hash, from_hash

from service.settings import admin_id, hashid_salt, alphabet

from hashids import Hashids

from django.contrib.auth.decorators import login_required


budget = {
    '30': 'до 1500 руб',
    '50': 'до 2500 руб',
    '75': 'до 3500 руб',
    '100': 'до 5000 руб',
    '150': 'от 5000 руб'
}


def quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name').capitalize()
        phone = request.POST.get('phone').replace('(', '').replace(')', '').replace('-', '')
        title = request.POST.get('title').capitalize()
        respond_price = request.POST.get('respond_price')
        message = request.POST.get('message')
        city = request.POST.get('city')[2:]
        address = request.POST.get('address')
        delivery = request.POST.get('delivery')
        date = request.POST.get('date')
        images = request.FILES.getlist('reference_images')
        if delivery == "need":
            delivery_info = "Требуется"
        else:
            delivery_info = "Не требуется"
        note = f'''Имя: {name};\nЗадание: {title};\nАдрес: {address};\nДоставка: {delivery_info};\nК дате: {date};\nБюджет: {budget.get(str(respond_price))};\nПодробнее: {message};'''
        # Для генерации сссылки
        hashids = Hashids(salt=hashid_salt, alphabet=alphabet, min_length=5)
        order = Order(name=name, phone=phone, status="NEW", note=note, respond_price=int(respond_price), city=city)
        order.save()
        # Сохраняем изображения для референсов
        if images:
            for image in images:
                ReferenceImage.objects.create(image=image, order=order)
        order_url = hashids.encode(order.id)
        order.order_url = order_url
        order.save()
        order_text = f'''🔴НОВОЕ ЗАДАНИЕ🔴\n{order.note}'''
        keyboard = json.dumps({"inline_keyboard": [[{"text": "Разместить задание", 'url': f'https://caketeam.herokuapp.com/orders/{order.id}'}]]})
        admin_staff_list = Staff.objects.filter(admin=True)
        for admin_staff in admin_staff_list:
            send_message(chat_id=int(admin_staff.telegram_id), text=order_text, reply_markup=keyboard)
        return redirect('quiz')
    else:
        return render(request, 'quiz/landing.html')


def order_for_client(request, order_url):
    # Находим id так как он идет после "-"
    order = get_object_or_404(Order, order_url=order_url)
    responds = Respond.objects.filter(order=order)
    context = {'order': order, 'responds': responds}
    return render(request, 'quiz/order_for_client.html', context)


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


def delete_order(request, order_id):
    order = Order.objects.filter(id=order_id)[0]
    order.delete()
    return redirect('orders')


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        max_responds = request.POST.get('max_responds')
        respond_price = request.POST.get('respond_price')
        send_all = request.POST.get('send_all')
        order.max_responds = max_responds
        order.respond_price = int(respond_price)
        order.status = "FIND"
        order.note = note
        order.save()
        # Внутренний код заявки в виде хэштега
        numb_of_order = order.set_numb_of_order()
        staff_list = Staff.objects.filter(active=True)
        for staff in staff_list:
            # Фильтрация по городам, если фильтра нет то рассылка по всем городам
            if order.city in staff.cities or staff.cities == '' or send_all is '1':
                hash_order_id = to_hash(order.id)
                hash_telegram_id = to_hash(int(staff.telegram_id))
                order_text = f'''Заявка {numb_of_order}\n{order.note.replace(";", "")}'''
                keyboard = json.dumps({"inline_keyboard": [[{"text": "Оставить заявку", 'url': f'http://127.0.0.1:8000/n/{hash_telegram_id}/{hash_order_id}'}]]})
                send_message(chat_id=int(staff.telegram_id), text=order_text, reply_markup=keyboard)
        return redirect('order_detail', order_id=order_id)
    else:
        notes = order.note
        responds = Respond.objects.filter(order=order)
        respond_price = order.respond_price

        # Если есть отклики
        if responds is not None:
            # Если уже выбран исполнитель
            if order.staff is not None:
                staff = order.staff
                respond = Respond.objects.filter(order=order, staff=staff)[0]
                return render(request, 'quiz/order_detail.html',
                              {'order': order, 'notes': notes, 'respond_price': respond_price, 'respond': respond})
            return render(request, 'quiz/order_detail.html', {'order': order, 'notes': notes, 'respond_price': respond_price, 'responds': responds})

        # Если нет откликов
        return render(request, 'quiz/order_detail.html', {'order': order, 'respond_price': respond_price, 'notes': notes})


# Для быстрого отклика для перехода из телеграма без логина
def order_respond(request, hash_order_id, hash_telegram_id):
    order_id = int(from_hash(hash_order_id))
    telegram_id = str(from_hash(hash_telegram_id))
    # Проверяем авторизован ли пользователь, если да то переводим на view понятным адоресом страницы
    if request.user.is_authenticated:
        return redirect('order_respond_login', order_id=order_id, telegram_id=telegram_id)
    order = get_object_or_404(Order, id=order_id)
    staff = Staff.objects.filter(telegram_id=telegram_id)[0]
    if request.method == 'POST':
        text = request.POST.get('message')
        price = request.POST.get('price')
        pin = request.POST.get('pin')
        # Так как несколько изображений
        images = request.FILES.getlist('images')
        if str(staff.pin) == str(pin):
            # Проверка на оставленный отзыв, если его нет, значит это первичное размещение отзыва и деньги списываются, а редактирование бесплатно
            if len(Respond.objects.filter(order=order, staff=staff)) == 0:
                # Нужно привязать к юзеру
                respond = Respond.objects.create(text=text, order=order, staff=staff, price=price)
                if images:
                    for image in images:
                        img = Image(image=image, respond=respond)
                        img.save()
                staff.balance = staff.balance - order.respond_price
                staff.save()
            # Редактирование уже оставленный отзыв
            else:
                respond = Respond.objects.filter(order=order, staff=staff)[0]
                respond.text = text
                respond.price = price
                respond.save()
                if images:
                    for image in images:
                        Image.objects.create(image=image, respond=respond)
            return redirect('order_respond', hash_order_id=hash_order_id, hash_telegram_id=hash_telegram_id)
        else:
            return redirect('quiz')   # Тут надо вызвать ошибку неправильного пина
    elif request.method == 'GET':
        if order.status == "FIND" or order.status == "WORK":
            notes = order.note.replace('-', '<br>')
            # Просмотры страницы
            if unique_view_of_order(order=order, staff=staff):
                order.views = order.views + 1
                order.save()
            # Для отображения количества откликов максимальных
            amount_responds = len(Respond.objects.filter(order=order))
            # Для проверки отклика по пину сотрудника через id чтобы не показывать пин на странице в коде
            num = staff.id

            # Проверка на оставленный отзыв данным юзером
            if len(Respond.objects.filter(order=order, staff=staff)) > 0:
                respond = Respond.objects.filter(order=order, staff=staff)[0]
            else:
                respond = None
            # Проверка достаточности баланса
            has_balance = staff.balance - order.respond_price >= 0
            context = {'order': order, 'staff': staff, 'notes': notes, 'num': num, 'amount_responds': amount_responds, 'respond': respond, 'has_balance': has_balance}
            return render(request, 'quiz/order_respond.html', context)
        else:
            raise Http404("Такой страницы не существует")


# Если юзер залогинен !! ДОБАВИТЬ декоратор
@login_required
def order_respond_login(request, order_id, telegram_id):
    order = get_object_or_404(Order, id=order_id)
    staff = Staff.objects.filter(telegram_id=telegram_id)[0]
    # Проверка на то что нужно быть залогиненым и смотреть можно только свою страницу
    if request.user.staff.telegram_id == str(telegram_id):
        if request.method == 'POST':
            text = request.POST.get('message')
            price = request.POST.get('price')
            pin = request.POST.get('pin')
            # Так как несколько изображений
            images = request.FILES.getlist('images')
            if str(staff.pin) == str(pin):
                # Проверка на оставленный отзыв, если его нет, значит это первичное размещение отзыва и деньги списываются, а редактирование бесплатно
                if len(Respond.objects.filter(order=order, staff=staff)) == 0:
                    # Нужно привязать к юзеру
                    respond = Respond.objects.create(text=text, order=order, staff=staff, price=price)
                    if images:
                        for image in images:
                            img = Image(image=image, respond=respond)
                            img.save()
                    staff.balance = staff.balance - order.respond_price
                    staff.save()
                # Редактирование уже оставленный отзыв
                else:
                    respond = Respond.objects.filter(order=order, staff=staff)[0]
                    respond.text = text
                    respond.price = price
                    respond.save()
                    if images:
                        for image in images:
                            Image.objects.create(image=image, respond=respond)
                return redirect('order_respond_login', order_id=order.id, telegram_id=staff.telegram_id)
            else:
                return redirect('quiz')   # Тут надо вызвать ошибку неправильного пина
        elif request.method == 'GET':
            if order.status == "FIND" or order.status == "WORK":
                notes = order.note.replace('-', '<br>')
                # Просмотры страницы
                if unique_view_of_order(order=order, staff=staff):
                    order.views = order.views + 1
                    order.save()
                # Для отображения количества откликов максимальных
                amount_responds = len(Respond.objects.filter(order=order))
                # Для проверки отклика по пину сотрудника через id чтобы не показывать пин на странице в коде
                num = staff.id

                # Проверка на оставленный отзыв данным юзером
                if len(Respond.objects.filter(order=order, staff=staff)) > 0:
                    respond = Respond.objects.filter(order=order, staff=staff)[0]
                else:
                    respond = None
                # Проверка достаточности баланса
                has_balance = staff.balance - order.respond_price >= 0
                context = {'order': order, 'staff': staff, 'notes': notes, 'num': num, 'amount_responds': amount_responds, 'respond': respond, 'has_balance': has_balance}
                return render(request, 'quiz/order_respond.html', context)
            else:
                raise Http404("Такой страницы не существует")
    else:
        raise Http404("Страницы нет")


@login_required
def profile_edit(request, telegram_id):
    staff = get_object_or_404(Staff, telegram_id=telegram_id)
    if request.user.staff == staff:
        if request.method == "GET":
            # Чтобы получить список городов из БД оформленной списком с разделителем в виде точки с запятой
            cities = staff.cities[:-1].split(";")
            context = {'staff': staff, 'cities': cities}
            return render(request, 'quiz/profile_edit.html', context=context)
    else:
        raise Http404("Такой страницы нет")



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


# удаление фото, принимает массив
def delete_foto(request):
    if request.method == "POST":
        # так как отправляет списком
        image_ids = request.POST.getlist('ids[]')
        for image_id in image_ids:
            image = Image.objects.get(id=image_id)
            image.delete()
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


def hint(request):
    if request.method == "POST":
        to = request.POST.get("to")
        respond_id = request.POST.get("id")
        if to == "wa":
            respond = Respond.objects.filter(id=respond_id)[0]
            respond.wa_hint = respond.wa_hint + 1
            respond.save()
        elif to == "insta":
            respond = Respond.objects.filter(id=respond_id)[0]
            respond.insta_hint = respond.insta_hint + 1
            respond.save()
        return HttpResponse('ok', content_type='text/plain', status=200)

def calc(request):
    if request.method == "POST":
        price = request.POST.get('price')
        print(price)
        return redirect('calc')
    else:
        return render(request, 'quiz/calc.html')


def edit_city(request):
    if request.method == "POST":
        telegram_id = request.POST.get("telegram_id")
        action = request.POST.get("action")
        city = request.POST.get("city")
        staff = Staff.objects.filter(telegram_id=telegram_id)[0]
        if action == "add":
            staff.cities = staff.cities + (city + ";")
            staff.save()
        elif action == "delete":
            staff.cities = staff.cities.replace(f'{city};', '')
            staff.save()
        return HttpResponse('ok', content_type='text/plain', status=200)



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