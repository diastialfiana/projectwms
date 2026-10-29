from django.urls import path

from .views import product_create, product_edit, product_list

urlpatterns = [
    path('', product_list, name='product_list'),
    path('new/', product_create, name='product_create'),
    path('<int:product_id>/edit/', product_edit, name='product_edit'),
]
