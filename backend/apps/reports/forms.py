from django import forms
from apps.products.models import Product
from django.utils import timezone

class ReportForm(forms.Form):
    REPORT_CHOICES = [
        ('current_stock', 'Текущие остатки товаров'),
        ('low_stock', 'Товары с остатком ниже минимального'),
        ('operations', 'Складские операции за период'),
        ('product_operations', 'Операции по конкретному товару'),
    ]
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_CHOICES,
        label='Тип отчета'
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        label='Формат отчета'
    )
    
    start_date = forms.DateField(
        label='Начальная дата',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        initial=timezone.now().replace(day=1)
    )
    end_date = forms.DateField(
        label='Конечная дата',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        initial=timezone.now()
    )
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label='Товар',
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get('report_type')
        
        if report_type in ['operations', 'product_operations']:
            if not cleaned_data.get('start_date') or not cleaned_data.get('end_date'):
                raise forms.ValidationError("Для этого отчета необходимо указать период")
            
            if cleaned_data['start_date'] > cleaned_data['end_date']:
                raise forms.ValidationError("Начальная дата не может быть больше конечной")
        
        if report_type == 'product_operations' and not cleaned_data.get('product'):
            raise forms.ValidationError("Для отчета по товару необходимо выбрать товар")
        
        return cleaned_data