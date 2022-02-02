from django.db import models
from django.conf import settings
from django.urls import reverse
from PIL import ImageOps, Image as PillowImage


class Staff(models.Model):
    avatar = models.ImageField(upload_to='avatars/', default='avatars/ava_F68lBxi.jpeg')
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
    cities = models.TextField(default='Все города', blank=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        super().save()
        img = PillowImage.open(self.avatar.path)
        img = ImageOps.exif_transpose(img)
        # Когда высота больше ширины
        if img.height > img.width:
            left = 0
            right = img.width
            top = (img.height - img.width) / 2
            bottom = (img.height + img.width) / 2
            img = img.crop((left, top, right, bottom))
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
            else:
                output_size = (img.width, img.width)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
        elif img.width > img.height:
            left = (img.width - img.height) / 2
            right = (img.width + img.height) / 2
            top = 0
            bottom = img.height
            img = img.crop((left, top, right, bottom))
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
            else:
                output_size = (img.height, img.height)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
        else:
            if img.height > 500 and img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
            else:
                output_size = (img.height, img.height)
                img.thumbnail(output_size)
                img.save(self.avatar.path)


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
    # Будем формировать для уникального url c помощью библиотеки hashids
    order_url = models.CharField(max_length=50, default="", unique=True)
    views = models.PositiveIntegerField(default=0)

    # Внутренний код заявки в виде хэштега
    def set_numb_of_order(self):
        numb_of_order = '#z' + '{}'.format(self.date.strftime('%Y'))[-2:] + '{}'.format(
            self.date.strftime('%m%d%H%M'))
        return numb_of_order

    def get_absolute_url(self):
        return reverse('order_for_client', args=[str(self.order_url)])

    def __str__(self):
        return '''{}, id:{}, {}'''.format(self.date.strftime('%d.%m.%Y %H:%M'), self.id, self.set_numb_of_order())


class OrderCounter(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orders")
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name="staffs")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order.set_numb_of_order(), self.staff.username


# Отклик на вакансию
class Respond(models.Model):
    text = models.TextField()
    date = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(Order, null=True, default='', on_delete=models.CASCADE, related_name='responds')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, default='', related_name='responds')
    price = models.CharField(max_length=50, default="")
    # Счетчик переходов от клмента, приемка через ajax
    wa_hint = models.PositiveIntegerField(default=0)
    insta_hint = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.staff.username} - {self.text}'


class Image(models.Model):
    image = models.ImageField(upload_to='responds/')
    respond = models.ForeignKey(Respond, null=True, default='', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return str(self.image)

    # Сохраянем изображение в соотношении 1:1, если разрешение большое то 1000на1000px, если меньше то по меньшей стороне
    def save(self, *args, **kwargs):
        super().save()
        img = PillowImage.open(self.image.path)
        # Для того чтобы картинка с телефона не поворачивалась
        img = ImageOps.exif_transpose(img)
        # Когда высота больше ширины
        if img.height > img.width:
            # обрезаем вверх и низ делая квадратной
            left = 0
            right = img.width
            top = (img.height - img.width) / 2
            bottom = (img.height + img.width) / 2
            img = img.crop((left, top, right, bottom))
            # Меняем разрешение на 1000х1000
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)
            else:
                output_size = (img.width, img.width)
                img.thumbnail(output_size)
                img.save(self.image.path)

        elif img.width > img.height:
            left = (img.width - img.height) / 2
            right = (img.width + img.height) / 2
            top = 0
            bottom = img.height
            img = img.crop((left, top, right, bottom))
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)
            else:
                output_size = (img.height, img.height)
                img.thumbnail(output_size)
                img.save(self.image.path)
        # если изображение квадратное
        else:
            if img.height > 1000 and img.width > 1000:
                output_size = (1000, 100)
                img.thumbnail(output_size)
                img.save(self.image.path)
            else:
                output_size = (img.height, img.height)
                img.thumbnail(output_size)
                img.save(self.image.path)


class Token(models.Model):
    token = models.CharField(max_length=30)

    def __str__(self):
        return 'token'