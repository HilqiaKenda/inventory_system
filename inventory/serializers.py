# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Supplier, Product, ProductSupplier, Inventory, 
    UserProfile, Cart, CartItem, Order, OrderItem
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'email', 'phone', 'address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['quantity', 'reserved_quantity', 'available_quantity', 'reorder_level', 'updated_at']
        read_only_fields = ['available_quantity', 'updated_at']

class ProductSupplierSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    
    class Meta:
        model = ProductSupplier
        fields = ['supplier', 'supplier_price', 'is_primary', 'created_at']
        read_only_fields = ['created_at']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    inventory = InventorySerializer(read_only=True)
    suppliers = ProductSupplierSerializer(source='productsupplier_set', many=True, read_only=True)
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 'description', 'price', 'sku', 
            'is_active', 'inventory', 'suppliers', 'in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
    category = serializers.StringRelatedField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'sku', 'is_active', 'in_stock']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'date_of_birth']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'username']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.in_stock:
                raise serializers.ValidationError("Product is out of stock.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist or is inactive.")

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        
        # Check if we have enough inventory
        if hasattr(self, 'initial_data') and 'product_id' in self.initial_data:
            try:
                product = Product.objects.get(id=self.initial_data['product_id'])
                if product.inventory.available_quantity < value:
                    raise serializers.ValidationError(
                        f"Only {product.inventory.available_quantity} items available in stock."
                    )
            except (Product.DoesNotExist, Inventory.DoesNotExist):
                pass
        
        return value

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
        read_only_fields = ['id', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    total_items = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'shipping_address', 'shipping_phone', 'subtotal', 'shipping_cost',
            'tax_amount', 'total_amount', 'items', 'total_items',
            'order_date', 'shipped_date', 'delivered_date', 'notes'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'order_date', 
            'shipped_date', 'delivered_date'
        ]

class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order listings"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_amount', 'total_items', 'order_date'
        ]

class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    shipping_address = serializers.CharField(max_length=500)
    shipping_phone = serializers.CharField(max_length=15)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = serializers.CharField(required=False, allow_blank=True)