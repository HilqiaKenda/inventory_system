from django.urls import path
from . import views
from .views import product_list, supplier_list,category_list

# inventory/urls.py

urlpatterns = [
    # Product URLs
    path('products/', product_list, name='product-list'),

    # Supplier URLs
    path('suppliers/', supplier_list, name='supplier-list'),

    # Category URLs
    path('categories/', category_list, name='category-list'),
    path('orders/create/', views.order_create, name='order-create'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),
    path('orders/', views.order_list, name='order_list'),
]
