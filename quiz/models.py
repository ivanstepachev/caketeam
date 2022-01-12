from django.db import models
from django.conf import settings


class Order(models.Model):
    name = models.CharField(max_length=200, default='')
    phone = models.CharField(max_length=15, default='')
    type_of_cake = models.CharField(max_length=10, default='')
    message = models.TextField(default='')
    note = models.TextField(default='', blank=True)

    def __str__(self):
        return self.name.capitalize()


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
    surname = models.CharField(max_length=15)
    telegram_id = models.IntegerField()
    admin = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.telegram_id


class Token(models.Model):
    token = models.CharField(max_length=30)

    def __str__(self):
        return 'token'