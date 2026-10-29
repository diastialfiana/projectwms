from django.contrib import admin

from .models import AuditLog, InventoryStock, StockMovement, StockOpname


@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity')
    search_fields = ('product__sku', 'warehouse__code')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'movement_type', 'quantity', 'reference_no', 'user', 'created_at')
    list_filter = ('movement_type',)
    search_fields = ('product__sku', 'reference_no')


@admin.register(StockOpname)
class StockOpnameAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'system_quantity', 'physical_quantity', 'difference', 'status')
    list_filter = ('status',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('activity', 'entity_type', 'entity_id', 'user', 'created_at')
    search_fields = ('activity', 'entity_type', 'entity_id')
