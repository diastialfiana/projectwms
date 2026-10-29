from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import ProductForm
from .models import Product


@login_required
def product_list(request):
    queryset = Product.objects.all()
    search = request.GET.get('q', '').strip()
    if search:
        queryset = queryset.filter(Q(sku__icontains=search) | Q(name__icontains=search))
    category = request.GET.get('category', '').strip()
    if category:
        queryset = queryset.filter(category__icontains=category)
    return render(request, 'products/product_list.html', {'products': queryset, 'search': search, 'category': category})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produk berhasil dibuat.')
        return redirect('product_list')
    return render(request, 'products/product_form.html', {'form': form, 'is_edit': False})


@login_required
def product_edit(request, product_id):
    product = Product.objects.get(pk=product_id)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produk berhasil diperbarui.')
        return redirect('product_list')
    return render(request, 'products/product_form.html', {'form': form, 'is_edit': True, 'product': product})
