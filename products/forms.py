from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'category', 'unit', 'minimum_stock', 'description', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_sku(self):
        sku = self.cleaned_data['sku'].strip()
        if Product.objects.filter(sku__iexact=sku).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('SKU sudah digunakan.')
        return sku

    def clean_minimum_stock(self):
        minimum = self.cleaned_data['minimum_stock']
        if minimum < 0:
            raise forms.ValidationError('Minimum stok tidak boleh negatif.')
        return minimum
