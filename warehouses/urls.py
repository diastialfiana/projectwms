from django.urls import path

from .views import warehouse_create, warehouse_edit, warehouse_list

urlpatterns = [
    path('', warehouse_list, name='warehouse_list'),
    path('new/', warehouse_create, name='warehouse_create'),
    path('<int:warehouse_id>/edit/', warehouse_edit, name='warehouse_edit'),
]
