from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from products.models import Product
from warehouses.models import Warehouse
from inventory.models import InventoryStock


class Command(BaseCommand):
    help = 'Seed demo products, warehouses, stock, and default user groups.'

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name='Administrators')
        warehouse_group, _ = Group.objects.get_or_create(name='Warehouse Users')

        admin, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True, 'email': 'admin@example.com'})
        admin.set_password('admin123')
        admin.groups.add(admin_group)
        admin.save()

        warehouse_user, _ = User.objects.get_or_create(username='warehouse', defaults={'is_staff': True, 'email': 'warehouse@example.com'})
        warehouse_user.set_password('warehouse123')
        warehouse_user.groups.add(warehouse_group)
        warehouse_user.save()

        products = [
            ('TUNA-001', 'Frozen Tuna Loin', 'Seafood', 'KG', Decimal('50')),
            ('TUNA-002', 'Tuna Steak', 'Seafood', 'KG', Decimal('30')),
            ('PACK-001', 'Packaging Box', 'Packaging', 'PCS', Decimal('100')),
            ('PACK-002', 'Plastic Packaging', 'Packaging', 'ROLL', Decimal('20')),
        ]
        for sku, name, category, unit, minimum in products:
            Product.objects.get_or_create(
                sku=sku,
                defaults={'name': name, 'category': category, 'unit': unit, 'minimum_stock': minimum}
            )

        warehouses = [
            ('WH-A', 'Gudang Bahan Baku', 'Jakarta', 'Raw material warehouse'),
            ('WH-B', 'Gudang Proses Produksi', 'Jakarta', 'Production warehouse'),
            ('WH-C', 'Gudang Barang Jadi', 'Surabaya', 'Finished goods warehouse'),
        ]
        for code, name, location, description in warehouses:
            Warehouse.objects.get_or_create(
                code=code,
                defaults={'name': name, 'location': location, 'description': description}
            )

        product = Product.objects.get(sku='TUNA-001')
        warehouse = Warehouse.objects.get(code='WH-A')
        InventoryStock.objects.get_or_create(product=product, warehouse=warehouse, defaults={'quantity': Decimal('500')})

        self.stdout.write(self.style.SUCCESS('Demo data created.'))
