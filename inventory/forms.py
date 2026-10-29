from decimal import Decimal

from django import forms

from products.models import Product
from warehouses.models import Warehouse


class StockInForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), label='Produk')
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True), label='Gudang')
    quantity = forms.DecimalField(min_value=Decimal('0.001'), max_digits=18, decimal_places=3, label='Kuantitas')
    reference_no = forms.CharField(max_length=80, required=False, label='Nomor Referensi')
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Catatan')


class StockOutForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), label='Produk')
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True), label='Gudang')
    quantity = forms.DecimalField(min_value=Decimal('0.001'), max_digits=18, decimal_places=3, label='Kuantitas')
    reference_no = forms.CharField(max_length=80, required=False, label='Nomor Referensi')
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Catatan')


class StockOpnameForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), label='Produk')
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True), label='Gudang')
    physical_quantity = forms.DecimalField(min_value=Decimal('0'), max_digits=18, decimal_places=3, label='Kuantitas Fisik')
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Catatan')
