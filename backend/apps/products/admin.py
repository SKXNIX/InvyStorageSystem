from django.contrib import admin
from .models import Product, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'location', 'quantity', 'min_stock')
    list_filter = ('category', 'unit')
    search_fields = ('name', 'category__name', 'location')
    list_editable = ('quantity', 'min_stock')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.site_header = "Управление складом"