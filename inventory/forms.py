from django import forms
from .models import Product, Supplier, Category, Order, Customer

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # fields = ['name', 'description', 'price', 'quantity', 'category', 'supplier']
        fields = ['name', 'description', 'price', 'quantity', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'contact_info': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'product', 'quantity']

# order = Order.objects.get(id=1)  # Replace with the actual ID you're testing
# print(order.status)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email']
