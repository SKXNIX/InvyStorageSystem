from decimal import Decimal
from django.urls import reverse
from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from apps.products.models import Product
from django.db.models import F, DecimalField, Sum
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView



class IndexView(TemplateView):
    template_name = 'core/index.html'


@login_required
def StartPage(request):
    # Общее количество наименований товаров
    total_products = Product.objects.count()
    all_product_names = list(Product.objects.values_list('name', flat=True))
    
    # Аннотируем total_quantity для всех запросов
    products = Product.objects.annotate(
        total_quantity=Coalesce(Sum('store__quantity'), Decimal('0.00'), output_field=DecimalField())
    )
    
    # Товары с низким остатком 
    low_stock_products = products.filter(
        total_quantity__lte=F('min_stock'),
        total_quantity__gt=0
    )
    low_stock_product_names = list(low_stock_products.values_list('name', flat=True))
    low_stock_count = low_stock_products.count()
    
    # Отсутствующие товары 
    out_of_stock_products = products.filter(
        total_quantity=0
    )
    out_of_stock_product_names = list(out_of_stock_products.values_list('name', flat=True))
    out_of_stock_count = out_of_stock_products.count()
    
    context = {
        'total_products': total_products,
        'all_product_names': all_product_names,
        'low_stock_products': low_stock_count,
        'low_stock_product_names': low_stock_product_names,
        'out_of_stock_products': out_of_stock_count,
        'out_of_stock_product_names': out_of_stock_product_names,
    }
    return render(request, 'core/start_page.html', context)




