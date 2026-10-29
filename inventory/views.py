from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import StockInForm, StockOpnameForm, StockOutForm
from .models import InventoryStock, StockMovement, StockOpname
from .services import approve_stock_opname, create_stock_opname, get_dashboard_stats, record_stock_in, record_stock_out


@login_required
def inventory_dashboard(request):
    return render(request, 'inventory/dashboard.html', {'stats': get_dashboard_stats()})


@login_required
def stock_in(request):
    form = StockInForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            movement, stock = record_stock_in(
                form.cleaned_data['product'],
                form.cleaned_data['warehouse'],
                form.cleaned_data['quantity'],
                request.user,
                reference_no=form.cleaned_data['reference_no'],
                notes=form.cleaned_data['notes'],
            )
            messages.success(request, f'Barang masuk berhasil dicatat: {movement.quantity} {movement.product.unit}.')
            return redirect('stock_movement_list')
        except ValidationError as exc:
            messages.error(request, str(exc))
    return render(request, 'inventory/stock_in_form.html', {'form': form})


@login_required
def stock_out(request):
    form = StockOutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            movement, stock = record_stock_out(
                form.cleaned_data['product'],
                form.cleaned_data['warehouse'],
                form.cleaned_data['quantity'],
                request.user,
                reference_no=form.cleaned_data['reference_no'],
                notes=form.cleaned_data['notes'],
            )
            messages.success(request, f'Barang keluar berhasil dicatat: {movement.quantity} {movement.product.unit}.')
            return redirect('stock_movement_list')
        except ValidationError as exc:
            messages.error(request, str(exc))
    return render(request, 'inventory/stock_out_form.html', {'form': form})


@login_required
def stock_movement_list(request):
    queryset = StockMovement.objects.select_related('product', 'warehouse', 'user')
    product_id = request.GET.get('product')
    warehouse_id = request.GET.get('warehouse')
    movement_type = request.GET.get('movement_type')
    search = request.GET.get('q', '').strip()

    if product_id:
        queryset = queryset.filter(product_id=product_id)
    if warehouse_id:
        queryset = queryset.filter(warehouse_id=warehouse_id)
    if movement_type:
        queryset = queryset.filter(movement_type=movement_type)
    if search:
        queryset = queryset.filter(Q(reference_no__icontains=search) | Q(product__sku__icontains=search))

    return render(request, 'inventory/movement_list.html', {'movements': queryset, 'search': search})


@login_required
def stock_opname_list(request):
    opnames = StockOpname.objects.select_related('product', 'warehouse', 'checked_by').all()
    return render(request, 'inventory/opname_list.html', {'opnames': opnames})


@login_required
def stock_opname_create(request):
    form = StockOpnameForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            create_stock_opname(
                form.cleaned_data['product'],
                form.cleaned_data['warehouse'],
                form.cleaned_data['physical_quantity'],
                request.user,
                notes=form.cleaned_data['notes'],
            )
            messages.success(request, 'Catatan stock opname dibuat.')
            return redirect('stock_opname_list')
        except ValidationError as exc:
            messages.error(request, str(exc))
    return render(request, 'inventory/opname_form.html', {'form': form})


@login_required
def stock_opname_approve(request, opname_id):
    opname = StockOpname.objects.get(pk=opname_id)
    try:
        approve_stock_opname(opname, request.user)
        messages.success(request, 'Penyesuaian stok opname berhasil disetujui.')
    except ValidationError as exc:
        messages.error(request, str(exc))
    return redirect('stock_opname_list')


@login_required
def inventory_reports(request):
    stock_rows = InventoryStock.objects.select_related('product', 'warehouse').all()
    low_stock = InventoryStock.objects.select_related('product').filter(quantity__lt=1)
    return render(request, 'inventory/reports.html', {'stock_rows': stock_rows, 'low_stock': low_stock})
