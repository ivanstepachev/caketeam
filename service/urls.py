from django.contrib import admin
from django.urls import path
from quiz import views as quiz_views
from django.conf.urls.static import static
from service import settings
from bot_token import token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_views.quiz, name="quiz"),
    path('<int:order_id>', quiz_views.order_respond, name="order_respond"),
    path('orders', quiz_views.orders, name="orders"),
    path('orders/<int:order_id>', quiz_views.order_detail, name="order_detail"),
    path('bot', quiz_views.bot, name="bot"),
    path('bot/setwebhook', quiz_views.setwebhook, name="setwebhook"),
    path('bot/deletewebhook', quiz_views.deletewebhook, name="deletewebhook"),
    path('reg/<str:chat_id>/<str:username>', quiz_views.registration, name="registration")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

