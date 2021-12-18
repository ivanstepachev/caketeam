from django.contrib import admin
from django.urls import path
from quiz import views as quiz_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_views.quiz, name="quiz"),
    path('orders', quiz_views.orders, name="orders"),
]
