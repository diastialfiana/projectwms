from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from inventory.models import AuditLog, InventoryStock, StockMovement, StockOpname
from products.models import Product
from warehouses.models import Warehouse


def ensure_default_groups(**kwargs):
    admin_group, _ = Group.objects.get_or_create(name='Administrators')
    warehouse_group, _ = Group.objects.get_or_create(name='Warehouse Users')

    all_models = [Product, Warehouse, InventoryStock, StockMovement, StockOpname, AuditLog]
    admin_permissions = []
    for model in all_models:
        for perm in Permission.objects.filter(content_type=ContentType.objects.get_for_model(model)):
            admin_permissions.append(perm)
    admin_group.permissions.set(admin_permissions)

    stock_permissions = Permission.objects.filter(
        content_type__in=[
            ContentType.objects.get_for_model(Product),
            ContentType.objects.get_for_model(Warehouse),
            ContentType.objects.get_for_model(InventoryStock),
            ContentType.objects.get_for_model(StockMovement),
            ContentType.objects.get_for_model(StockOpname),
        ]
    )
    warehouse_group.permissions.set(stock_permissions)
