# Traditional Django views (updated for new models)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import (
    ProductForm, SupplierForm, CategoryForm, UserUpdateForm, UserProfileForm,
    CartItemForm, OrderForm, OrderStatusUpdateForm, CustomUserCreationForm
)
from .models import (
    OrderItem, Product, Supplier, Category, Order, UserProfile, Cart, CartItem, Inventory
)

def homepage(request):
    """Homepage with featured products and categories"""
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'inventory/homepage.html', context)

# Product Views
def product_list(request):
    """List products with search and filtering"""
    query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.filter(is_active=True).select_related('category', 'inventory')
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': query,
        'selected_category': category_id,
    }
    return render(request, 'inventory/product_list.html', context)

def product_detail(request, pk):
    """Product detail view"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'inventory'), 
        pk=pk, 
        is_active=True
    )
    
    context = {
        'product': product,
        'can_add_to_cart': request.user.is_authenticated and product.in_stock,
    }
    return render(request, 'inventory/product_detail.html', context)

@user_passes_test(lambda u: u.is_staff)
def product_create(request):
    """Create new product (staff only)"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            # Create inventory record
            Inventory.objects.create(product=product, quantity=0)
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('product-detail', pk=product.pk)
    else:
        form = ProductForm()
    
    return render(request, 'inventory/product_form.html', {
        'form': form, 
        'form_title': 'Create Product'
    })

@user_passes_test(lambda u: u.is_staff)
def product_update(request, pk):
    """Update product (staff only)"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('product-detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/product_form.html', {
        'form': form, 
        'form_title': 'Edit Product',
        'product': product
    })

@user_passes_test(lambda u: u.is_staff)
def product_delete(request, pk):
    """Delete product (staff only)"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False  # Soft delete
        product.save()
        messages.success(request, f'Product "{product.name}" deactivated successfully.')
        return redirect('product-list')
    
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

# Category Views
def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@user_passes_test(lambda u: u.is_staff)
def category_create(request):
    """Create new category (staff only)"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('category-list')
    else:
        form = CategoryForm()
    
    return render(request, 'inventory/category_form.html', {
        'form': form, 
        'form_title': 'Create Category'
    })

@user_passes_test(lambda u: u.is_staff)
def category_update(request, pk):
    """Update category (staff only)"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('category-list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'inventory/category_form.html', {
        'form': form, 
        'form_title': 'Edit Category',
        'category': category
    })

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

# Supplier Views
def supplier_list(request):
    """List all suppliers"""
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@user_passes_test(lambda u: u.is_staff)
def supplier_create(request):
    """Create new supplier (staff only)"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" created successfully.')
            return redirect('supplier-list')
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form, 
        'form_title': 'Create Supplier'
    })

@user_passes_test(lambda u: u.is_staff)
def supplier_update(request, pk):
    """Update supplier (staff only)"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Supplier "{supplier.name}" updated successfully.')
            return redirect('supplier-detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form, 
        'form_title': 'Edit Supplier',
        'supplier': supplier
    })

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier-list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'

# User Profile Views
@login_required
def user_profile(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'inventory/user_profile.html', {'profile': profile})

@login_required
def user_profile_edit(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user-profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    return render(request, 'inventory/user_profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# Cart Views
@login_required
def cart_view(request):
    """View cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product')
    
    return render(request, 'inventory/cart.html', {
        'cart': cart,
        'cart_items': cart_items
    })

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if not product.in_stock:
        messages.error(request, 'Product is out of stock.')
        return redirect('product-detail', pk=product_id)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < product.inventory.available_quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Added another "{product.name}" to cart.')
        else:
            messages.warning(request, f'Cannot add more "{product.name}". Only {product.inventory.available_quantity} available.')
    else:
        messages.success(request, f'Added "{product.name}" to cart.')
    
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item, product=cart_item.product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed "{product_name}" from cart.')
    return redirect('cart')

@login_required
def clear_cart_view(request):
    """Clear all items from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared successfully.')
    return redirect('cart')

# Order Views
@login_required
def order_list(request):
    """List user's orders"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/order_list.html', {'page_obj': page_obj})

@login_required
def order_detail(request, pk):
    """Order detail view"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'), 
        pk=pk, 
        user=request.user
    )
    return render(request, 'inventory/order_detail.html', {'order': order})

@login_required
@transaction.atomic
def checkout(request):
    """Checkout process"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.total_price
            order.total_amount = cart.total_price  # Add shipping/tax calculation as needed
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price
                )
                
                # Reserve inventory
                inventory = cart_item.product.inventory
                inventory.reserved_quantity += cart_item.quantity
                inventory.save()
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('order-detail', pk=order.pk)
    else:
        form = OrderForm()
    
    return render(request, 'inventory/checkout.html', {
        'form': form,
        'cart': cart
    })

# Admin Order