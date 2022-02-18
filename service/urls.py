from django.contrib import admin
from django.urls import path
from quiz import views as quiz_views
from django.conf.urls.static import static
from service import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', quiz_views.login_view_redirect, name='login_redirect'),
    path('login', quiz_views.login_view, name='login'),
    path('login/', quiz_views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='quiz/change_password.html'), name='password_change'),
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view(template_name='quiz/change_password_done.html'), name='password_change_done'),

    path('', quiz_views.landing, name="landing"),
    path('quiz', quiz_views.quiz, name="quiz"),
    path('profile/<str:telegram_id>', quiz_views.profile, name="profile"),
    path('a/profile/<str:telegram_id>', quiz_views.profile_edit, name="profile_edit"),
    path('a/profile/<str:telegram_id>/info', quiz_views.profile_edit_info, name="profile_edit_info"),
    path('a/profile/<str:telegram_id>/contacts', quiz_views.profile_edit_contacts, name="profile_edit_contacts"),
    path('a/city', quiz_views.edit_city, name="edit_city"),
    path('n/<str:hash_telegram_id>/<str:hash_order_id>', quiz_views.order_respond, name="order_respond"),
    path('a/<str:telegram_id>/<int:order_id>', quiz_views.order_respond_login, name="order_respond_login"),
    path('a/orders', quiz_views.staff_orders, name="staff_orders"),
    path('confirm/', quiz_views.confirm, name="confirm"),
    path('orders', quiz_views.orders, name="orders"),
    path('order/delete/<int:order_id>', quiz_views.delete_order, name="delete_order"),
    path('orders/<int:order_id>', quiz_views.order_detail, name="order_detail"),
    path('orders/done/<int:order_id>', quiz_views.order_done, name="order_done"),
    # выбор отклика
    path('respond/<int:respond_id>', quiz_views.respond_choice, name="respond_choice"),
    path('respond/cancel/<int:respond_id>', quiz_views.respond_cancel, name="respond_cancel"),
    path('respond/delete/<int:respond_id>', quiz_views.respond_delete, name="respond_delete"),

    path('review/done/<str:order_url>', quiz_views.review_done, name="review_done"),
    path('review/undone/<str:order_url>', quiz_views.review_undone, name="review_undone"),
    path('bot', quiz_views.bot, name="bot"),

    path('staff', quiz_views.staff_list, name="staff_list"),
    path('staff/activate/<str:chat_id>', quiz_views.staff_activate, name="staff_activate"),
    path('staff/deactivate/<str:chat_id>', quiz_views.staff_deactivate, name="staff_deactivate"),
    path('staff/delete/<str:chat_id>', quiz_views.staff_delete, name="staff_delete"),
    path('bot/setwebhook', quiz_views.setwebhook, name="setwebhook"),
    path('bot/deletewebhook', quiz_views.deletewebhook, name="deletewebhook"),
    path('hint', quiz_views.hint, name="hint"),
    path('reg/<str:chat_id>/<str:username>', quiz_views.registration, name="registration"),
    path('delete/foto', quiz_views.delete_foto, name="delete_foto"),
    path('calc', quiz_views.calc, name="calc"),
    path('<str:order_url>', quiz_views.order_for_client, name="order_for_client")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'quiz.views.handler404'
handler500 = 'quiz.views.handler500'