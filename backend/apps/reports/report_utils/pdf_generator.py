import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from apps.store.models import StockReceipt, Dispatch
from apps.products.models import Product
from django.db.models import F

# Регистрируем шрифт с поддержкой кириллицы
pdfmetrics.registerFont(TTFont('DejaVuSans', 'backend/apps/reports/fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'backend/apps/reports/fonts/DejaVuSans-Bold.ttf'))

def generate_pdf_response(filename, title, headers, data):
    """Генерирует PDF документ с таблицей"""
    buffer = io.BytesIO()
    
    # Создаем PDF документ
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        title=title,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Стили для текста с использованием кириллического шрифта
    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'DejaVuSans-Bold'
    styles['Normal'].fontName = 'DejaVuSans'
    
    # Подготовка элементов документа
    elements = []
    
    # Добавляем заголовок
    elements.append(Paragraph(title, styles['Title']))
    
    # Преобразуем данные в формат для таблицы
    table_data = [headers] + data
    
    # Создаем таблицу
    table = Table(table_data)
    
    # Стили таблицы
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
    ]))
    
    elements.append(table)
    
    # Собираем документ
    doc.build(elements)
    
    # Получаем PDF из буфера
    pdf = buffer.getvalue()
    buffer.close()
    
    # Создаем HTTP ответ
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    response.write(pdf)
    
    return response

def generate_current_stock_pdf():
    """Генерация PDF отчета текущих остатков"""
    queryset = Product.objects.select_related('category').annotate(
        current_quantity=F('quantity')
    ).order_by('name')
    
    # Подготавливаем данные
    headers = [
        'Товар', 'Категория', 'Количество', 
        'Единица измерения', 'Место хранения', 'Мин. остаток'
    ]
    
    data = []
    for product in queryset:
        data.append([
            product.name,
            product.category.name,
            str(product.quantity),
            product.unit,
            product.location,
            str(product.min_stock)
        ])
    
    return generate_pdf_response(
        filename="current_stock",
        title="Отчет по текущим остаткам",
        headers=headers,
        data=data
    )


def generate_current_stock_pdf():
    """Генерация PDF отчета текущих остатков"""
    queryset = Product.objects.select_related('category').annotate(
        current_quantity=F('quantity')
    ).order_by('name')
    
    # Подготавливаем данные
    headers = [
        'Товар', 'Категория', 'Количество', 
        'Единица измерения', 'Место хранения', 'Мин. остаток'
    ]
    
    data = []
    for product in queryset:
        data.append([
            product.name,
            product.category.name,
            str(product.quantity),
            product.unit,
            product.location,
            str(product.min_stock)
        ])
    
    return generate_pdf_response(
        filename="current_stock",
        title="Отчет по текущим остаткам",
        headers=headers,
        data=data
    )

def generate_low_stock_pdf():
    """Генерация PDF отчета товаров с низким остатком"""
    queryset = Product.objects.filter(quantity__lte=F('min_stock'))
    
    headers = [
        'Товар', 'Категория', 'Текущий остаток',
        'Минимальный остаток', 'Разница', 'Единица измерения'
    ]
    
    data = []
    for product in queryset:
        data.append([
            product.name,
            product.category.name,
            str(product.quantity),
            str(product.min_stock),
            str(product.quantity - product.min_stock),
            product.unit
        ])
    
    return generate_pdf_response(
        filename="low_stock",
        title="Отчет по товарам с низким остатком",
        headers=headers,
        data=data
    )

def generate_operations_pdf(start_date, end_date):
    """Генерация PDF отчета по операциям за период"""
    headers = [
        'Дата', 'Тип операции', 'Товар', 
        'Количество', 'Ед. изм.', 'Номер накладной', 
        'Поставщик', 'Статус'
    ]
    
    data = []
    
    # Поступления
    for receipt in StockReceipt.objects.filter(receipt_date__range=[start_date, end_date]):
        data.append([
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
        data.append([
            dispatch.dispatch_date.strftime('%d.%m.%Y'),
            'Отгрузка',
            dispatch.product.name,
            str(dispatch.quantity),
            dispatch.product.unit,
            dispatch.invoice_number,
            dispatch.recipient,
            dispatch.get_status_display()
        ])
    
    return generate_pdf_response(
        filename=f"operations_{start_date}_{end_date}",
        title=f"Отчет по операциям с {start_date} по {end_date}",
        headers=headers,
        data=data
    )

def generate_product_operations_pdf(product, start_date, end_date):
    """Генерация PDF отчета по операциям с конкретным товаром"""
    headers = [
        'Дата', 'Тип операции', 'Количество', 
        'Ед. изм.', 'Номер накладной', 'Поставщик', 
        'Статус', 'Комментарий'
    ]
    
    data = []
    
    # Поступления
    receipts = StockReceipt.objects.filter(
        product=product,
        receipt_date__range=[start_date, end_date]
    ).select_related('supplier')
    
    for receipt in receipts:
        data.append([
            receipt.receipt_date.strftime('%d.%m.%Y'),
            'Поступление',
            str(receipt.quantity),
            receipt.product.unit,
            receipt.invoice_number,
            receipt.supplier.name if receipt.supplier else '',
            receipt.get_status_display(),
            receipt.comment or ''
        ])
    
    # Отгрузки
    dispatches = Dispatch.objects.filter(
        product=product,
        dispatch_date__range=[start_date, end_date]
    )
    
    for dispatch in dispatches:
        data.append([
            dispatch.dispatch_date.strftime('%d.%m.%Y'),
            'Отгрузка',
            str(dispatch.quantity),
            dispatch.product.unit,
            dispatch.invoice_number,
            dispatch.recipient,
            dispatch.get_status_display(),
            dispatch.comment or ''
        ])
    
    return generate_pdf_response(
        filename=f"product_{product.id}_operations_{start_date}_{end_date}",
        title=f"Отчет по операциям с товаром {product.name} ({start_date} - {end_date})",
        headers=headers,
        data=data
    )