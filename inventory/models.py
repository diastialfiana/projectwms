from decimal import Decimal

from django.conf import settings
from django.db import models as db_models

from products.models import Product
from warehouses.models import Warehouse


class InventoryStock(db_models.Model):
    product = db_models.ForeignKey(Product, on_delete=db_models.PROTECT, related_name='stock_entries')
    warehouse = db_models.ForeignKey(Warehouse, on_delete=db_models.PROTECT, related_name='stock_entries')
    quantity = db_models.DecimalField(max_digits=18, decimal_places=3, default=Decimal('0'))
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            db_models.UniqueConstraint(fields=['product', 'warehouse'], name='uniq_product_warehouse_stock'),
            db_models.CheckConstraint(condition=db_models.Q(quantity__gte=Decimal('0')), name='inventory_quantity_non_negative'),
        ]
        indexes = [db_models.Index(fields=['product', 'warehouse']), db_models.Index(fields=['quantity'])]

    def __str__(self):
        return f'{self.product.sku} @ {self.warehouse.code}: {self.quantity}'


class StockMovement(db_models.Model):
    MOVEMENT_IN = 'IN'
    MOVEMENT_OUT = 'OUT'
    MOVEMENT_ADJUSTMENT = 'ADJUSTMENT'
    MOVEMENT_CHOICES = [
        (MOVEMENT_IN, 'Stock In'),
        (MOVEMENT_OUT, 'Stock Out'),
        (MOVEMENT_ADJUSTMENT, 'Adjustment'),
    ]

    product = db_models.ForeignKey(Product, on_delete=db_models.PROTECT, related_name='movements')
    warehouse = db_models.ForeignKey(Warehouse, on_delete=db_models.PROTECT, related_name='movements')
    movement_type = db_models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = db_models.DecimalField(max_digits=18, decimal_places=3)
    reference_no = db_models.CharField(max_length=80, blank=True)
    notes = db_models.TextField(blank=True)
    user = db_models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=db_models.PROTECT, related_name='stock_movements')
    created_at = db_models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [db_models.Index(fields=['movement_type', 'created_at']), db_models.Index(fields=['product', 'warehouse'])]

    def __str__(self):
        return f'{self.movement_type} {self.product.sku} @ {self.warehouse.code}'


class StockOpname(db_models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    product = db_models.ForeignKey(Product, on_delete=db_models.PROTECT, related_name='opname_entries')
    warehouse = db_models.ForeignKey(Warehouse, on_delete=db_models.PROTECT, related_name='opname_entries')
    system_quantity = db_models.DecimalField(max_digits=18, decimal_places=3, default=Decimal('0'))
    physical_quantity = db_models.DecimalField(max_digits=18, decimal_places=3, default=Decimal('0'))
    difference = db_models.DecimalField(max_digits=18, decimal_places=3, default=Decimal('0'))
    checked_by = db_models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=db_models.PROTECT, related_name='stock_opnames')
    checked_at = db_models.DateTimeField(auto_now_add=True)
    status = db_models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = db_models.TextField(blank=True)
    approved_by = db_models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=db_models.PROTECT, related_name='approved_stock_opnames', null=True, blank=True)
    approved_at = db_models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-checked_at']

    def save(self, *args, **kwargs):
        self.difference = self.physical_quantity - self.system_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.sku} @ {self.warehouse.code} ({self.status})'


class AuditLog(db_models.Model):
    user = db_models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=db_models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    activity = db_models.CharField(max_length=150)
    entity_type = db_models.CharField(max_length=80)
    entity_id = db_models.CharField(max_length=100, blank=True)
    old_value = db_models.TextField(blank=True, default='')
    new_value = db_models.TextField(blank=True, default='')
    created_at = db_models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [db_models.Index(fields=['entity_type', 'entity_id']), db_models.Index(fields=['created_at'])]

    def __str__(self):
        return f'{self.activity} - {self.entity_type}'
