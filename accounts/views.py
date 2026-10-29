from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import models
from django.shortcuts import redirect, render

from inventory.models import InventoryStock, StockMovement
from products.models import Product
from warehouses.models import Warehouse


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user is not None:
            login(request, user)
            messages.success(request, 'Login berhasil.')
            return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Anda telah logout.')
    return redirect('login')


@login_required
def dashboard(request):
    products = Product.objects.filter(is_active=True).count()
    warehouses = Warehouse.objects.filter(is_active=True).count()
    stock_rows = InventoryStock.objects.count()
    latest_in = StockMovement.objects.filter(movement_type='IN').select_related('product', 'warehouse', 'user').order_by('-created_at')[:5]
    latest_out = StockMovement.objects.filter(movement_type='OUT').select_related('product', 'warehouse', 'user').order_by('-created_at')[:5]
    low_stock = InventoryStock.objects.select_related('product', 'warehouse').filter(quantity__lt=models.F('product__minimum_stock'))

    return render(
        request,
        'dashboard.html',
        {
            'product_count': products,
            'warehouse_count': warehouses,
            'stock_count': stock_rows,
            'latest_in': latest_in,
            'latest_out': latest_out,
            'low_stock': low_stock,
        },
    )
