from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from products.models import Product
from warehouses.models import Warehouse

from .models import AuditLog, InventoryStock, StockMovement, StockOpname


def _log_activity(user, activity, entity_type, entity_id, old_value='', new_value=''):
    AuditLog.objects.create(
        user=user,
        activity=activity,
        entity_type=entity_type,
        entity_id=str(entity_id),
        old_value=str(old_value),
        new_value=str(new_value),
    )


def get_or_create_stock(product, warehouse):
    with transaction.atomic():
        stock = InventoryStock.objects.select_for_update().filter(product=product, warehouse=warehouse).first()
        if stock is None:
            stock = InventoryStock.objects.create(product=product, warehouse=warehouse, quantity=Decimal('0'))
        return stock


def record_stock_in(product, warehouse, quantity, user, reference_no='', notes=''):
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation as exc:
        raise ValidationError('Kuantitas tidak valid.') from exc

    if qty <= 0:
        raise ValidationError('Kuantitas masuk harus lebih besar dari nol.')
    if not product.is_active or not warehouse.is_active:
        raise ValidationError('Produk atau gudang tidak aktif.')

    with transaction.atomic():
        product_row = Product.objects.select_for_update().get(pk=product.pk)
        warehouse_row = Warehouse.objects.select_for_update().get(pk=warehouse.pk)
        stock = InventoryStock.objects.select_for_update().filter(product_id=product_row.pk, warehouse_id=warehouse_row.pk).first()
        if stock is None:
            stock = InventoryStock.objects.create(product=product_row, warehouse=warehouse_row, quantity=Decimal('0'))

        old_quantity = Decimal(str(stock.quantity))
        stock.quantity = old_quantity + qty
        stock.save(update_fields=['quantity', 'updated_at'])

        movement = StockMovement.objects.create(
            product=product_row,
            warehouse=warehouse_row,
            movement_type=StockMovement.MOVEMENT_IN,
            quantity=qty,
            reference_no=reference_no,
            notes=notes,
            user=user,
        )
        _log_activity(user, 'Stock In', 'InventoryStock', stock.pk, old_value=old_quantity, new_value=stock.quantity)
        _log_activity(user, 'Movement In', 'StockMovement', movement.pk, old_value='', new_value=movement.quantity)
        return movement, stock


def record_stock_out(product, warehouse, quantity, user, reference_no='', notes=''):
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation as exc:
        raise ValidationError('Kuantitas tidak valid.') from exc

    if qty <= 0:
        raise ValidationError('Kuantitas keluar harus lebih besar dari nol.')
    if not product.is_active or not warehouse.is_active:
        raise ValidationError('Produk atau gudang tidak aktif.')

    with transaction.atomic():
        product_row = Product.objects.select_for_update().get(pk=product.pk)
        warehouse_row = Warehouse.objects.select_for_update().get(pk=warehouse.pk)
        stock = InventoryStock.objects.select_for_update().filter(product_id=product_row.pk, warehouse_id=warehouse_row.pk).first()
        if stock is None:
            raise ValidationError('Saldo stok belum tersedia.')

        if stock.quantity < qty:
            raise ValidationError('Stok tidak mencukupi.')

        old_quantity = Decimal(str(stock.quantity))
        stock.quantity = old_quantity - qty
        stock.save(update_fields=['quantity', 'updated_at'])

        movement = StockMovement.objects.create(
            product=product_row,
            warehouse=warehouse_row,
            movement_type=StockMovement.MOVEMENT_OUT,
            quantity=qty,
            reference_no=reference_no,
            notes=notes,
            user=user,
        )
        _log_activity(user, 'Stock Out', 'InventoryStock', stock.pk, old_value=old_quantity, new_value=stock.quantity)
        _log_activity(user, 'Movement Out', 'StockMovement', movement.pk, old_value='', new_value=movement.quantity)
        return movement, stock


def create_stock_opname(product, warehouse, physical_quantity, checked_by, notes=''):
    try:
        physical = Decimal(str(physical_quantity))
    except InvalidOperation as exc:
        raise ValidationError('Kuantitas fisik tidak valid.') from exc

    if physical < 0:
        raise ValidationError('Kuantitas fisik tidak boleh negatif.')

    stock = InventoryStock.objects.filter(product=product, warehouse=warehouse).first()
    system_quantity = Decimal(str(stock.quantity)) if stock else Decimal('0')
    opname = StockOpname.objects.create(
        product=product,
        warehouse=warehouse,
        system_quantity=system_quantity,
        physical_quantity=physical,
        notes=notes,
        checked_by=checked_by,
    )
    _log_activity(checked_by, 'Stock Opname Created', 'StockOpname', opname.pk, old_value='', new_value=str(opname.difference))
    return opname


def approve_stock_opname(opname, approved_by):
    with transaction.atomic():
        opname = StockOpname.objects.select_for_update().get(pk=opname.pk)
        stock = InventoryStock.objects.select_for_update().filter(product=opname.product, warehouse=opname.warehouse).first()
        if stock is None:
            stock = InventoryStock.objects.create(product=opname.product, warehouse=opname.warehouse, quantity=Decimal('0'))

        delta = opname.physical_quantity - opname.system_quantity
        if delta != 0:
            old_quantity = Decimal(str(stock.quantity))
            if old_quantity + delta < 0:
                raise ValidationError('Penyesuaian stok menyebabkan nilai negatif.')
            stock.quantity = old_quantity + delta
            stock.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                product=opname.product,
                warehouse=opname.warehouse,
                movement_type=StockMovement.MOVEMENT_ADJUSTMENT,
                quantity=abs(delta),
                reference_no=f'OP-{opname.pk}',
                notes=f'Adjustment from stock opname: {opname.notes}',
                user=approved_by,
            )
            _log_activity(approved_by, 'Stock Adjustment', 'InventoryStock', stock.pk, old_value=old_quantity, new_value=stock.quantity)

        opname.status = StockOpname.STATUS_APPROVED
        opname.approved_by = approved_by
        opname.approved_at = timezone.now()
        opname.save(update_fields=['status', 'approved_by', 'approved_at'])
        _log_activity(approved_by, 'Stock Opname Approved', 'StockOpname', opname.pk, old_value='', new_value=str(opname.difference))
        return opname


def get_dashboard_stats():
    from django.db.models import Count, Sum

    low_stock = InventoryStock.objects.select_related('product').filter(quantity__lt=F('product__minimum_stock'))
    latest_in = StockMovement.objects.filter(movement_type=StockMovement.MOVEMENT_IN).select_related('product', 'warehouse', 'user').order_by('-created_at')[:5]
    latest_out = StockMovement.objects.filter(movement_type=StockMovement.MOVEMENT_OUT).select_related('product', 'warehouse', 'user').order_by('-created_at')[:5]

    return {
        'product_count': Product.objects.filter(is_active=True).count(),
        'warehouse_count': Warehouse.objects.filter(is_active=True).count(),
        'stock_count': InventoryStock.objects.count(),
        'latest_in': latest_in,
        'latest_out': latest_out,
        'low_stock': low_stock,
    }
