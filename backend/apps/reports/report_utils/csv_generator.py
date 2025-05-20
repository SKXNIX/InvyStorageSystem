import csv
from decimal import Decimal
from django.db.models.functions import Coalesce
import pandas as pd
from django.http import HttpResponse
from apps.store.models import Store, StockReceipt, Dispatch
from apps.products.models import Product
from django.db.models import F, DecimalField, Sum

def generate_current_stock():
    # Получаем данные из модели Product
    queryset = Product.objects.select_related('category').annotate(
        current_quantity=Coalesce(Sum('store__quantity'), Decimal('0.00'), output_field=DecimalField())
    ).order_by('name')
    
    # Создаем HTTP ответ
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': 'attachment; filename="current_stock.csv"'},
    )
    
    # Добавляем BOM для корректного отображения в Excel
    response.write('\ufeff'.encode('utf-8'))
    
    # Создаем writer
    writer = csv.writer(response, delimiter=';')
    
    # Заголовки
    writer.writerow([
        'Товар', 'Категория', 'Количество', 
        'Единица измерения', 'Место хранения', 'Мин. остаток'
    ])
    
    # Данные
    for product in queryset:
        writer.writerow([
            product.name,
            product.category.name,
            product.current_quantity,
            product.unit,
            product.location,
            product.min_stock
        ])
    
    return response

def generate_low_stock():
    queryset = Product.objects.annotate(
        current_quantity=Coalesce(Sum('store__quantity'), Decimal('0.00'), output_field=DecimalField())
    ).filter(current_quantity__lte=F('min_stock'))
    
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': 'attachment; filename="low_stock.csv"'},
    )
    
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow([
        'Товар', 'Категория', 'Текущий остаток',
        'Минимальный остаток', 'Разница', 'Единица измерения'
    ])
    
    for product in queryset:
        writer.writerow([
            product.name,
            product.category.name,
            str(product.current_quantity),
            str(product.min_stock),
            str(product.current_quantity - product.min_stock),
            product.unit
        ])
    
    return response

def generate_operations(start_date, end_date):
    # Создаем HTTP-ответ с правильными настройками для Excel
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'operations_{start_date}_{end_date}.csv'},
    )
    
    # Добавляем BOM для корректного отображения кириллицы в Excel
    response.write('\ufeff'.encode('utf-8'))
    
    # Создаем writer с правильным разделителем (запятая или точка с запятой)
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    # Заголовки столбцов
    writer.writerow([
        'Дата', 'Тип операции', 'Товар', 
        'Количество', 'Ед. изм.', 'Номер накладной', 
        'Поставщик', 'Статус'
    ])
    
    # Поступления
    for receipt in StockReceipt.objects.filter(receipt_date__range=[start_date, end_date]):
        writer.writerow([
            receipt.receipt_date.strftime('%d.%m.%Y'),
            'Поступление',
            receipt.product.name,
            str(receipt.quantity),
            receipt.product.unit,
            receipt.invoice_number,
            receipt.supplier.name if receipt.supplier else '',
            receipt.get_status_display()
        ])
    
    # Отгрузки
    for dispatch in Dispatch.objects.filter(dispatch_date__range=[start_date, end_date]):
        writer.writerow([
            dispatch.dispatch_date.strftime('%d.%m.%Y'),
            'Отгрузка',
            dispatch.product.name,
            str(dispatch.quantity),
            dispatch.product.unit,
            dispatch.invoice_number,
            dispatch.recipient,
            dispatch.get_status_display()
        ])
    
    return response

def generate_product_operations(product, start_date, end_date):
    """Генерация CSV отчета по операциям с конкретным товаром"""
    from apps.store.models import StockReceipt, Dispatch
    
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'product_{product.id}_operations_{start_date}_{end_date}.csv'},
    )
    response.write('\ufeff'.encode('utf-8'))  # BOM для Excel
    
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    # Заголовки
    writer.writerow([
        'Дата', 'Тип операции', 'Количество', 
        'Ед. изм.', 'Номер накладной', 'Поставщик', 
        'Статус', 'Комментарий'
    ])
    
    # Поступления
    receipts = StockReceipt.objects.filter(
        product=product,
        receipt_date__range=[start_date, end_date]
    ).select_related('supplier')
    
    for receipt in receipts:
        writer.writerow([
            receipt.receipt_date.strftime('%d.%m.%Y'),
            'Поступление',
            receipt.quantity,
            receipt.product.unit,
            receipt.invoice_number,
            receipt.supplier.name if receipt.supplier else '',
            receipt.get_status_display(),
            receipt.comment
        ])
    
    # Отгрузки
    dispatches = Dispatch.objects.filter(
        product=product,
        dispatch_date__range=[start_date, end_date]
    )
    
    for dispatch in dispatches:
        writer.writerow([
            dispatch.dispatch_date.strftime('%d.%m.%Y'),
            'Отгрузка',
            dispatch.quantity,
            dispatch.product.unit,
            dispatch.invoice_number,
            dispatch.recipient,
            dispatch.get_status_display(),
            dispatch.comment
        ])
    
    return response