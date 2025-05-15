from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    User, использующийся в проекте.
    Кастомный класс пользователя
    с расширенными свойствами
    """
    ROLE_CHOICES = (
        ('superadmin', 'Суперадмин'),
        ('admin', 'Админ'),
        ('storekeeper', 'Кладовщик'),
    )
    username = models.CharField(verbose_name='Логин', max_length=150, unique=True)
    password = models.CharField(verbose_name='Пароль', max_length=128)
    full_name = models.CharField(verbose_name='ФИО', max_length=255, blank=True, null=True)
    role = models.CharField(verbose_name='Должность', max_length=20, choices=ROLE_CHOICES, default='storekeeper')
    avatar = models.ImageField(verbose_name='Аватар', upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'