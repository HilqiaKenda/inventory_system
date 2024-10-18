from django.contrib import admin
from .models import Product, Supplier, Customer, Order, Inventory

# Register your models here.
# inventory/admin.py

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Inventory)
