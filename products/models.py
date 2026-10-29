from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=80, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=80, blank=True)
    unit = models.CharField(max_length=30)
    minimum_stock = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['sku']), models.Index(fields=['name']), models.Index(fields=['is_active'])]

    def __str__(self):
        return f'{self.sku} - {self.name}'
