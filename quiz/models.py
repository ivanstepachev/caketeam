from django.db import models
from django.conf import settings


class Staff(models.Model):
    username = models.CharField(max_length=25, default='')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default='')
    name = models.CharField(max_length=15, default='')
    surname = models.CharField(max_length=15, default='')
    city = models.CharField(max_length=15, default='')
    telegram_id = models.CharField(max_length=15)
    phone = models.CharField(max_length=15, default='')
    instagram = models.CharField(max_length=20, default='')
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    pin = models.CharField(max_length=4, blank=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)


class Order(models.Model):
    STATUS_CHOICE = (
        ("NEW", "new"),
        ("FIND", "find"),
        ("WORK", "work"),
        ("DONE", "done"),
    )

    name = models.CharField(max_length=200, default='')
    phone = models.CharField(max_length=15, default='')
    type_of_cake = models.CharField(max_length=10, default='')
    message = models.TextField(default='')
    max_responds = models.IntegerField(default=5)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default="NEW")
    note = models.TextField(default='')
    staff = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.PROTECT, related_name="orders")
    respond_price = models.IntegerField(default=50)

    # Внутренний код заявки в виде хэштега
    def set_numb_of_order(self):
        numb_of_order = '#z' + '{}'.format(self.date.strftime('%Y'))[-2:] + '{}'.format(
            self.date.strftime('%m%d%H%M'))
        return numb_of_order

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.date.strftime('%d.%m.%Y %H:%M'), self.name, self.phone, self.message)


# Отклик на вакансию
class Respond(models.Model):
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, null=True, default='', on_delete=models.CASCADE, related_name='responds')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, default='', related_name='responds')
    price = models.CharField(max_length=50, default="")

    def __str__(self):
        return f'{self.staff.username} - {self.text}'


class Image(models.Model):
    image = models.ImageField(upload_to='responds/')
    respond = models.ForeignKey(Respond, null=True, default='', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return str(self.image)


class Token(models.Model):
    token = models.CharField(max_length=30)

    def __str__(self):
        return 'token'