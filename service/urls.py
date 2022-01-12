from django.contrib import admin
from django.urls import path
from quiz import views as quiz_views
from django.conf.urls.static import static
from service import settings
from bot_token import token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_views.quiz, name="quiz"),
    path('orders', quiz_views.orders, name="orders"),
    path('orders/<int:order_id>', quiz_views.order_detail, name="order_detail"),
    path('bot', quiz_views.bot, name="bot")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

