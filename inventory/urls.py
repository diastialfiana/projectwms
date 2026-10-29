from django.urls import path

from .views import (
    inventory_dashboard,
    inventory_reports,
    stock_in,
    stock_movement_list,
    stock_opname_approve,
    stock_opname_create,
    stock_opname_list,
    stock_out,
)

urlpatterns = [
    path('', inventory_dashboard, name='inventory_dashboard'),
    path('stock-in/', stock_in, name='stock_in'),
    path('stock-out/', stock_out, name='stock_out'),
    path('movements/', stock_movement_list, name='stock_movement_list'),
    path('opnames/', stock_opname_list, name='stock_opname_list'),
    path('opnames/new/', stock_opname_create, name='stock_opname_create'),
    path('opnames/<int:opname_id>/approve/', stock_opname_approve, name='stock_opname_approve'),
    path('reports/', inventory_reports, name='inventory_reports'),
]
