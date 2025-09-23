# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API URLs
urlpatterns = [
    # Authentication will be handled by Django REST framework's built-in views
    # Products (Public access)
    path('products/', views.ProductListAPIView.as_view(), name='api-product-list'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api-product-detail'),
    
    # Categories (Public access)
    path('categories/', views.CategoryListAPIView.as_view(), name='api-category-list'),
    
    # User Profile (Authenticated users only)
    path('profile/', views.UserProfileAPIView.as_view(), name='api-user-profile'),
    
    # Cart (Authenticated users only)
    path('cart/', views.CartAPIView.as_view(), name='api-cart'),
    path('cart/items/', views.CartItemListCreateAPIView.as_view(), name='api-cart-items'),
    path('cart/items/<int:pk>/', views.CartItemUpdateDestroyAPIView.as_view(), name='api-cart-item-detail'),
    path('cart/clear/', views.clear_cart, name='api-clear-cart'),
    
    # Orders (Authenticated users only)
    path('orders/', views.OrderListCreateAPIView.as_view(), name='api-order-list'),
    path('orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='api-order-detail'),
    path('orders/stats/', views.user_order_stats, name='api-user-order-stats'),
    
    # Admin-only endpoints
    path('admin/orders/', views.AdminOrderListAPIView.as_view(), name='api-admin-order-list'),
    path('admin/orders/<int:pk>/', views.AdminOrderDetailAPIView.as_view(), name='api-admin-order-detail'),
    path('admin/orders/<int:pk>/status/', views.update_order_status, name='api-update-order-status'),
    path('admin/dashboard/', views.admin_dashboard_stats, name='api-admin-dashboard'),
]
