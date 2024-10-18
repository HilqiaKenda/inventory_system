from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm, SupplierForm, CategoryForm
from .models import Product, Supplier, Category

from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import DeleteView, DetailView
# Create your views here.

# inventory/views.py
def homepage(request):
    return render(request, 'inventory/homepage.html')

def product_list(request):
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
            return redirect('product-list')  # Redirect to the product list page
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
    # return render(request, 'category-list', {'form': form, 'form_title': 'Edit Supplier'})

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier-list')

# Supplier Delete View
# class SupplierDeleteView(DeleteView):
#     model = Supplier
#     template_name = 'supplier_confirm_delete.html'
#     success_url = reverse_lazy('supplier-list')  # Redirect after deletion

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
