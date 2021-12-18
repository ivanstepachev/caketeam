from django.contrib import admin
from django.urls import path
from quiz import views as quiz_views
from service import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_views.quiz, name="quiz"),
    path('orders', quiz_views.orders, name="orders"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

