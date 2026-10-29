from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import WarehouseForm
from .models import Warehouse


@login_required
def warehouse_list(request):
    queryset = Warehouse.objects.all()
    search = request.GET.get('q', '').strip()
    if search:
        queryset = queryset.filter(Q(code__icontains=search) | Q(name__icontains=search) | Q(location__icontains=search))
    return render(request, 'warehouses/warehouse_list.html', {'warehouses': queryset, 'search': search})


@login_required
def warehouse_create(request):
    form = WarehouseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Gudang berhasil dibuat.')
        return redirect('warehouse_list')
    return render(request, 'warehouses/warehouse_form.html', {'form': form, 'is_edit': False})


@login_required
def warehouse_edit(request, warehouse_id):
    warehouse = Warehouse.objects.get(pk=warehouse_id)
    form = WarehouseForm(request.POST or None, instance=warehouse)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Gudang berhasil diperbarui.')
        return redirect('warehouse_list')
    return render(request, 'warehouses/warehouse_form.html', {'form': form, 'is_edit': True, 'warehouse': warehouse})
