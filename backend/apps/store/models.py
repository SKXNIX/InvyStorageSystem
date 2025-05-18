from django.db import models
from django.core.exceptions import ValidationError

from apps.products.models import Product
from apps.custom_auth.models import CustomUser

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Store(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product',)

    def __str__(self):
        return f'{self.product.name} - Количество: {self.quantity} {self.product.unit}'


class Place(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительское место'
        )
    identifier = models.SlugField(unique=True, help_text='Уникальный идентификатор (например, A1-B2)')
    TYPE_CHOICES = [
        ('zone', 'Зона'),
        ('section', 'Секция'),
        ('shelf', 'Полка'),
        ('cell', 'Ячейка'),
        ]
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='zone',
        verbose_name='Тип места'
        )
    capacity = models.IntegerField(default=0, verbose_name='Вместимость, кг/м³')
    temperature = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Температурный режим'
        )

    def __str__(self):
        return f'{self.name} ({self.type})'

    def clean(self):
        if self.parent:
            ancestor = self.parent
            while not ancestor is None:
                if ancestor == self:
                    raise ValidationError("Ошибка: циклическая зависимость")
                ancestor = ancestor.parent
        return super().clean()


class Supplier(models.Model):

    name = models.CharField(max_length=255, verbose_name='Название компании')
    contact_person = models.CharField(max_length=255, verbose_name='Контактное лицо', blank=True, null=True)
    email = models.EmailField(verbose_name='Электронная почта', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True, null=True)
    address = models.TextField(verbose_name='Адрес', blank=True, null=True)
    website = models.URLField(verbose_name='Веб-сайт', blank=True, null=True)
    notes = models.TextField(verbose_name='Примечания', blank=True, null=True)

    def __str__(self):
        return self.name


class StockReceipt(models.Model):
    STATUS_CHOICES = [
        ('received', 'Получено'),
        ('pending', 'Ожидается'),
        ('cancelled', 'Отменено'),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_date = models.DateField()
    invoice_number = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_receipts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'

class Dispatch(models.Model):
    STATUS_CHOICES = [
        ('dispatched', 'Отгружено'),
        ('pending', 'Ожидается'),
        ('cancelled', 'Отменено'),
        ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    dispatch_date = models.DateField()
    invoice_number = models.CharField(max_length=100, unique=True)
    recipient = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if self.pk:
            original = Dispatch.objects.get(pk=self.pk)
            if original.status == 'dispatched' and self.status != 'dispatched':
                if not user or not user.role == 'superadmin':
                    raise ValueError("Нельзя изменить статус отгрузки, которая уже была отгружена")
                store = Store.objects.get(product=self.product)
                store.quantity += original.quantity
                store.save()
        if self.status == 'dispatched':
            store = Store.objects.get(product=self.product)
            if store.quantity >= self.quantity:
                store.quantity -= self.quantity
                store.save()
            else:
                raise ValueError(f'Недостаточно товара на склад: требуется {self.quantity}, доступно {store.quantity}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.quantity} {self.product.unit} - {self.dispatch_date}'
