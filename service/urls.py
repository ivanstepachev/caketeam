from django.contrib import admin
from django.urls import path
from quiz import views as quiz_views
from django.conf.urls.static import static
from service import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_views.quiz, name="quiz"),
    path('<int:order_id>/<str:telegram_id>', quiz_views.order_respond, name="order_respond"),
    path('orders', quiz_views.orders, name="orders"),
    path('orders/<int:order_id>', quiz_views.order_detail, name="order_detail"),
    path('orders/done/<int:order_id>', quiz_views.order_done, name="order_done"),
    path('responds/<str:chat_id>', quiz_views.responds_list, name="responds_list"),
    # выбор отклика
    path('respond/<int:respond_id>', quiz_views.respond_choice, name="respond_choice"),
    path('respond/delete/<int:respond_id>', quiz_views.respond_delete, name="respond_delete"),
    path('bot', quiz_views.bot, name="bot"),

    path('staff', quiz_views.staff_list, name="staff_list"),
    path('staff/activate/<str:chat_id>', quiz_views.staff_activate, name="staff_activate"),
    path('staff/deactivate/<str:chat_id>', quiz_views.staff_deactivate, name="staff_deactivate"),
    path('staff/delete/<str:chat_id>', quiz_views.staff_delete, name="staff_delete"),
    path('bot/setwebhook', quiz_views.setwebhook, name="setwebhook"),
    path('bot/deletewebhook', quiz_views.deletewebhook, name="deletewebhook"),
    path('reg/<str:chat_id>/<str:username>', quiz_views.registration, name="registration"),
    path('delete/foto', quiz_views.delete_foto, name="delete_foto"),
    path('calc', quiz_views.calc, name="calc"),
    path('<str:order_url>', quiz_views.order_for_client, name="order_for_client")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

