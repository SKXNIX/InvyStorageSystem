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
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='storekeeper')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'