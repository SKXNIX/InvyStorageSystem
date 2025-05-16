from django.db import models
from django.core.exceptions import ValidationError


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
