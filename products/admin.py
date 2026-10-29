from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'unit', 'minimum_stock', 'is_active')
    search_fields = ('sku', 'name')
    list_filter = ('is_active', 'category')
