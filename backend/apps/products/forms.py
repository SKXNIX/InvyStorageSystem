from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        labels = {
            'name': 'Наименование',
            'category': 'Категория',
            'unit': 'Единица измерения',
            'description': 'Описание',
            'location': 'Место хранения',
            'min_stock': 'Минимальный остаток',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Название',
        }