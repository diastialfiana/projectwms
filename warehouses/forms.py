from django import forms

from .models import Warehouse


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['code', 'name', 'location', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if Warehouse.objects.filter(code__iexact=code).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Kode gudang sudah digunakan.')
        return code
