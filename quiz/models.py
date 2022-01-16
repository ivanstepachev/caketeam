from django.db import models
from django.conf import settings


class Order(models.Model):
    name = models.CharField(max_length=200, default='')
    phone = models.CharField(max_length=15, default='')
    type_of_cake = models.CharField(max_length=10, default='')
    message = models.TextField(default='')

    # def __str__(self):
    #     return self.name.capitalize()


class Note(models.Model):
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, null=True, default='', on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return f'{self.date} {self.text}'


# Отклик на вакансию
class Respond(models.Model):
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, null=True, default='', on_delete=models.CASCADE, related_name='responds')

    def __str__(self):
        return f'{self.date} {self.text}'


class Image(models.Model):
    image = models.ImageField(upload_to='responds/')
    respond = models.ForeignKey(Respond, null=True, default='', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return str(self.image)


class Staff(models.Model):
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=20, default='')
    name = models.CharField(max_length=15)
    surname = models.CharField(max_length=15)
    telegram_id = models.CharField(max_length=15)
    admin = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    pin = models.CharField(max_length=4, blank=True)

    def __str__(self):
        return self.username


class Token(models.Model):
    token = models.CharField(max_length=30)

    def __str__(self):
        return 'token'