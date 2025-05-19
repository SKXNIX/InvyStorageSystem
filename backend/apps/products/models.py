from django.db import models
from django.db.models import Q, F

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        app_label = 'products'  
    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('шт', 'Штуки'),
        ('кг', 'Килограммы'),
        ('л', 'Литры'),
        ('уп', 'Упаковки'),
        ('м', 'Метры'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'products'  # Добавьте это
        
    def __str__(self):
        return self.name
    
    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.min_stock:
            return 'critical'
        return 'in_stock'