from django.urls import path
from . import views
from .views import supplier_list, supplier_create, supplier_update, category_create, category_update, SupplierDetailView
from .views import product_list, product_detail, product_create, product_update, product_delete
from .views import category_create, category_update, category_list, CategoryDeleteView, SupplierDeleteView

# inventory/urls.py

urlpatterns = [
    # Product URLs
    path('products/', product_list, name='product-list'),

    # Supplier URLs
    path('suppliers/', supplier_list, name='supplier-list'),

    # Category URLs
    path('categories/', category_list, name='category-list'),

    # path('customers/', views.customer_list, name='customer-form'),
    # path('orders/', views.order_list, name='order-list'),
    # path('orders/', views.order_form, name='order-form'),
    
    path('customers/create/', views.customer_create, name='customer-create'),
    path('customers/', views.customer_list, name='customer-list'),
    path('orders/create/', views.order_create, name='order-create'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),
    path('orders/', views.order_list, name='order-list'),
        path('orders/<int:order_id>/', views.order_detail, name='order-detail'),
    # path('order/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    #    path('order/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
