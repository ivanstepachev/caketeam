from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=200, default='')
    phone = models.CharField(max_length=15, default='')
    type_of_cake = models.CharField(max_length=10, default='')
    message = models.TextField(default='')

    def __str__(self):
        return self.name.capitalize()

