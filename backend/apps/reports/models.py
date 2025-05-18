from django.db import models
from django.conf import settings

class Report(models.Model):
    REPORT_TYPES = [
        ('current_stock', 'Текущие остатки'),
        ('low_stock', 'Низкие остатки'),
        ('operations', 'Складские операции'),
        ('product_history', 'История товара'),
    ]
    
    FORMATS = [
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]
    
    user_id = models.IntegerField()  # Вместо ForeignKey
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    format = models.CharField(max_length=10, choices=FORMATS)
    created_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.get_report_type_display()} ({self.get_format_display()})"