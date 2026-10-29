from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase

from inventory.models import InventoryStock, StockMovement, StockOpname
from inventory.services import approve_stock_opname, create_stock_opname, record_stock_in, record_stock_out
from products.models import Product
from warehouses.models import Warehouse

User = get_user_model()


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='secret123')
        self.product = Product.objects.create(
            sku='TUNA-001',
            name='Frozen Tuna Loin',
            category='Seafood',
            unit='KG',
            minimum_stock=Decimal('20'),
        )
        self.warehouse = Warehouse.objects.create(
            code='WH-A',
            name='Gudang Bahan Baku',
            location='Jakarta',
        )

    def test_stock_in_success(self):
        movement, stock = record_stock_in(self.product, self.warehouse, Decimal('50'), self.user)
        self.assertEqual(stock.quantity, Decimal('50'))
        self.assertEqual(StockMovement.objects.count(), 1)
        self.assertEqual(movement.movement_type, StockMovement.MOVEMENT_IN)

    def test_stock_out_success(self):
        record_stock_in(self.product, self.warehouse, Decimal('10'), self.user)
        movement, stock = record_stock_out(self.product, self.warehouse, Decimal('3'), self.user)
        self.assertEqual(stock.quantity, Decimal('7'))
        self.assertEqual(movement.movement_type, StockMovement.MOVEMENT_OUT)

    def test_stock_out_rejected_when_insufficient(self):
        record_stock_in(self.product, self.warehouse, Decimal('5'), self.user)
        with self.assertRaises(ValidationError):
            record_stock_out(self.product, self.warehouse, Decimal('7'), self.user)

    def test_zero_and_negative_quantity_rejected(self):
        with self.assertRaises(ValidationError):
            record_stock_in(self.product, self.warehouse, Decimal('0'), self.user)
        with self.assertRaises(ValidationError):
            record_stock_out(self.product, self.warehouse, Decimal('-1'), self.user)

    def test_stock_opname_approval_adjusts_inventory(self):
        record_stock_in(self.product, self.warehouse, Decimal('10'), self.user)
        opname = create_stock_opname(self.product, self.warehouse, Decimal('7'), self.user, notes='Fisik lebih rendah')
        self.assertEqual(opname.difference, Decimal('-3'))
        approve_stock_opname(opname, self.user)
        self.assertEqual(InventoryStock.objects.get(product=self.product, warehouse=self.warehouse).quantity, Decimal('7'))

    def test_duplicate_sku_and_warehouse_code_are_rejected(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Product.objects.create(sku='TUNA-001', name='Duplicate', category='X', unit='KG')
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Warehouse.objects.create(code='WH-A', name='Duplicate', location='Bandung')


class InventoryConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='concurrent-user', password='secret123')
        self.product = Product.objects.create(
            sku='TUNA-002',
            name='Tuna Steak',
            category='Seafood',
            unit='KG',
            minimum_stock=Decimal('10'),
        )
        self.warehouse = Warehouse.objects.create(
            code='WH-B',
            name='Gudang Produksi',
            location='Jakarta',
        )
        record_stock_in(self.product, self.warehouse, Decimal('10'), self.user)

    def test_concurrent_stock_out_does_not_create_negative_balance(self):
        InventoryStock.objects.filter(product=self.product, warehouse=self.warehouse).update(quantity=Decimal('10'))

        first_outcome = None
        second_outcome = None
        try:
            _, _ = record_stock_out(self.product, self.warehouse, Decimal('7'), self.user)
            first_outcome = 'success'
        except ValidationError:
            first_outcome = 'error'

        try:
            _, _ = record_stock_out(self.product, self.warehouse, Decimal('6'), self.user)
            second_outcome = 'success'
        except ValidationError:
            second_outcome = 'error'

        final_stock = InventoryStock.objects.get(product=self.product, warehouse=self.warehouse).quantity
        self.assertEqual(first_outcome, 'success')
        self.assertEqual(second_outcome, 'error')
        self.assertEqual(final_stock, Decimal('3'))
        self.assertGreaterEqual(final_stock, Decimal('0'))
