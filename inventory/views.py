# views.py
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import (
    Category, Supplier, Product, UserProfile, Cart, CartItem, Order, OrderItem
)
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer, ProductListSerializer,
    UserSerializer, CartSerializer, CartItemSerializer, OrderSerializer,
    OrderListSerializer, CreateOrderSerializer
)
from inventory import models

# Authentication required for all views
class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only to the owner
        return obj.user == request.user

# Product Views (Public - no auth required for reading)
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'inventory')
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'inventory')
    serializer_class = ProductSerializer

# Category Views (Public)
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# User Profile Views
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Cart Views
class CartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related('product')

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        product = get_object_or_404(Product, id=serializer.validated_data['product_id'])
        
        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        if existing_item:
            # Update quantity instead of creating new item
            existing_item.quantity += serializer.validated_data['quantity']
            existing_item.save()
            return existing_item
        else:
            serializer.save(cart=cart, product=product)

class CartItemUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart = get_object_or_404(Cart, user=self.request.user)
        return CartItem.objects.filter(cart=cart)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from user's cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_200_OK)

# Order Views
class OrderListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate totals
        subtotal = cart.total_price
        shipping_cost = serializer.validated_data.get('shipping_cost', 0)
        tax_amount = serializer.validated_data.get('tax_amount', 0)
        total_amount = subtotal + shipping_cost + tax_amount

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            shipping_phone=serializer.validated_data['shipping_phone'],
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total_amount=total_amount,
            notes=serializer.validated_data.get('notes', '')
        )

        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            
            # Update inventory (reserve items)
            inventory = cart_item.product.inventory
            inventory.reserved_quantity += cart_item.quantity
            inventory.save()

        # Clear cart after successful order creation
        cart.items.all().delete()

        # Return created order
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

# Admin-only views for order management
class AdminOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.all().select_related('user').prefetch_related('items__product')
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        user_id = self.request.query_params.get('user', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset

class AdminOrderDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def update_order_status(request, pk):
    """Update order status - Admin only"""
    order = get_object_or_404(Order, pk=pk)
    new_status = request.data.get('status')
    
    if new_status not in dict(Order.STATUS_CHOICES):
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    old_status = order.status
    order.status = new_status
    
    # Handle status-specific logic
    if new_status == Order.STATUS_SHIPPED and old_status != Order.STATUS_SHIPPED:
        from django.utils import timezone
        order.shipped_date = timezone.now()
        
    elif new_status == Order.STATUS_DELIVERED and old_status != Order.STATUS_DELIVERED:
        from django.utils import timezone
        order.delivered_date = timezone.now()
        
        # Move reserved inventory to sold (reduce actual quantity)
        for item in order.items.all():
            inventory = item.product.inventory
            inventory.quantity -= item.quantity
            inventory.reserved_quantity -= item.quantity
            inventory.save()
            
    elif new_status == Order.STATUS_CANCELLED and old_status != Order.STATUS_CANCELLED:
        # Release reserved inventory
        for item in order.items.all():
            inventory = item.product.inventory
            inventory.reserved_quantity -= item.quantity
            inventory.save()
    
    order.save()
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)

# Statistics and Dashboard Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_order_stats(request):
    """Get user's order statistics"""
    user = request.user
    orders = Order.objects.filter(user=user)
    
    stats = {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status=Order.STATUS_PENDING).count(),
        'completed_orders': orders.filter(status=Order.STATUS_DELIVERED).count(),
        'total_spent': sum(order.total_amount for order in orders),
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard_stats(request):
    """Get admin dashboard statistics"""
    from django.db.models import Sum, Count
    
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status=Order.STATUS_PENDING).count(),
        'total_revenue': Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'total_users': User.objects.count(),
        'total_products': Product.objects.filter(is_active=True).count(),
        'low_stock_products': Product.objects.filter(
            inventory__quantity__lte=models.F('inventory__reorder_level')
        ).count(),
    }
    
    return Response(stats)