from django import forms
from .models import Product, Category

class ProductFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Поиск по наименованию, категории или месту хранения'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория'
    )
    
    availability = forms.ChoiceField(
        choices=[
            ('all', 'Все'),
            ('available', 'В наличии'),
            ('out_of_stock', 'Отсутствующие')
        ],
        required=False,
        label='Наличие',
        initial='all'
    )
    
    critical_stock = forms.BooleanField(
        required=False,
        label='Только критический запас'
    )
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'min_stock': forms.NumberInput(attrs={'min': 0}),
        }
        labels = {
            'name': 'Наименование',
            'category': 'Категория',
            'quantity': 'Количество', 
            'unit': 'Единица измерения',
            'description': 'Описание',
            'location': 'Место хранения',
            'min_stock': 'Минимальный остаток',
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Название',
        }