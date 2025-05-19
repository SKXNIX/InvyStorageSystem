from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from apps.products.models import Category, Product
from apps.products.forms import ProductForm, CategoryForm, ProductFilterForm
from django.core.paginator import Paginator
from django.db.models import Q

def product_list(request):
    # Получаем параметры фильтрации
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    availability = request.GET.get('availability', 'all')
    critical = request.GET.get('critical', False)
    
    # Фильтрация товаров
    products = Product.objects.all().select_related('category')
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(location__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if availability == 'available':
        products = products.filter(quantity__gt=0)
    elif availability == 'out_of_stock':
        products = products.filter(quantity=0)
    
    if critical:
        products = products.filter(quantity__lte=F('min_stock'))
    
    # Пагинация
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем все категории для фильтра
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'selected_availability': availability,
        'critical_checked': 'checked' if critical else '',
    }
    return render(request, 'products/list.html', context)

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            #messages.success(request, f'Товар "{product.name}" успешно добавлен!')
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('products:list')
    return render(request, 'products/confirm_delete.html', {'product': product})

# Аналогичные представления для Category (category_list, category_create и т.д.)

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/category_form.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'products/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('products:category_list')
    return render(request, 'products/category_confirm_delete.html', {'category': category})