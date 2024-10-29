from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm, SupplierForm, CategoryForm, Order, CustomerForm, OrderForm
from .models import Product, Supplier, Category, Order, Customer
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView

# Create your views here.

# inventory/views.py
def homepage(request):
    return render(request, 'inventory/homepage.html')

def product_list(request):
    query = request.GET.get('product_request')
        
    if query:
        products = Product.objects.filter(name__icontains = query)
    else:
        products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            if request.is_ajax():
                return JsonResponse({'success': True, 'redirect_url': '/products/'})
            return redirect('product-list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'form_title': 'Create Product'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product-list')
    return render(request, 'product_confirm_delete.html', {'product': product})

# Product views
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product-list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'form_title': 'Create Product'})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product-list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'form_title': 'Edit Product'})

# Supplier views
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier-list')
    else:
        form = SupplierForm()
    return render(request, 'supplier_form.html', {'form': form, 'form_title': 'Create Supplier'})

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier-list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'supplier_form.html', {'form': form, 'form_title': 'Edit Supplier'})

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier-list')

class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'supplier_detail.html'
    context_object_name = 'supplier'

# Category views
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category-list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form, 'form_title': 'Create Category'})

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category-list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form, 'form_title': 'Edit Category'})
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category-list')

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer-list')  # Adjust this as needed
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            customer_name = form.cleaned_data['customer_name']
            customer, created = Customer.objects.get_or_create(name=customer_name)

            order = form.save(commit=False)
            order.customer = customer
            order.save()

            return redirect('order-list')
    else:
        form = OrderForm()
    return render(request, 'order_form.html', {'form': form})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_detail.html', {'order': order})

def order_list(request):
    query_order = request.GET.get('order_request')
    
    if query_order:
        orders = Order.objects.filter(id__icontains=query_order)
        orders = Order.objects.filter(customer__name__icontains=query_order)
        orders = Order.objects.filter(quantity__icontains=query_order)
    else:
        orders = Order.objects.all()
    return render(request, 'inventory/order_list.html', {'orders': orders})

def admin_required(function):
    return user_passes_test(lambda u: u.is_superuser)(function)

@admin_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return redirect('order_list')
    return render(request, 'inventory/update_order_status.html', {'order': order})

@admin_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        print(f"Received new status: {new_status} for Order ID: {order_id}")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            print(f"Updated Order ID: {order_id} to status: {order.status}")
            return redirect('order_list')
        else:
            print("Invalid status received.")
    
    return render(request, 'inventory/update_order_status.html', {'order': order})
