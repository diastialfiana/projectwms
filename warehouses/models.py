from django.db import models


class Warehouse(models.Model):
    code = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['code']), models.Index(fields=['is_active'])]

    def __str__(self):
        return f'{self.code} - {self.name}'
