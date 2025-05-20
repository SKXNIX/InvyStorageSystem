from django.contrib import admin
from .models import Product, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_total_quantity', 'unit', 'location', 'quantity', 'min_stock')
    list_filter = ('category', 'unit')
    search_fields = ('name', 'category__name', 'location')
    list_editable = ('min_stock',)

    @admin.display(description='Общее количество')
    def get_total_quantity(self, obj):
        return obj.quantity  # Вызываем свойство модели

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.site_header = "Управление складом"