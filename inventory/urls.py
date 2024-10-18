from django.urls import path
from . import views
from .views import supplier_list, supplier_create, supplier_update, category_create, category_update, SupplierDetailView
from .views import product_list, product_detail, product_create, product_update, product_delete
from .views import category_create, category_update, category_list, CategoryDeleteView, SupplierDeleteView

# inventory/urls.py

urlpatterns = [
    # Product URLs
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('products/create/', product_create, name='product-create'),
    path('products/<int:pk>/update/', product_update, name='product-update'),
    path('products/<int:pk>/delete/', product_delete, name='product-delete'),
    path('products/new/', views.product_create, name='product-create'),
    path('products/<int:pk>/edit/', views.product_update, name='product-update'),
    
    # Supplier URLs
    path('suppliers/', supplier_list, name='supplier-list'),
    path('suppliers/create/', supplier_create, name='supplier-create'),
    path('suppliers/<int:pk>/edit/', supplier_update, name='supplier-update'),
    path('suppliers/new/', views.supplier_create, name='supplier-create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier-update'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier-delete'),
    
    # Category URLs
    path('categories/', category_list, name='category-list'),
    path('categories/create/', category_create, name='category-create'),
    path('categories/<int:pk>/edit/', category_update, name='category-update'),
    path('products/', product_list, name='product-list'),  
    path('categories/new/', views.category_create, name='category-create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),

]
