from django.contrib import admin
from .models import Product, Supplier, Customer, Order, Inventory

# Register your models here.
# inventory/admin.py


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'order_date')
    actions = ['set_status_pending', 'set_status_shipped', 'set_status_delivered']

    def set_status_pending(self, request, queryset):
        queryset.update(status='P')
        self.message_user(request, "Selected orders have been marked as Pending.")
    set_status_pending.short_description = "Mark selected orders as Pending"

    def set_status_shipped(self, request, queryset):
        queryset.update(status='S')
        self.message_user(request, "Selected orders have been marked as Shipped.")
    set_status_shipped.short_description = "Mark selected orders as Shipped"

    def set_status_delivered(self, request, queryset):
        queryset.update(status='D')
        self.message_user(request, "Selected orders have been marked as Delivered.")
    set_status_delivered.short_description = "Mark selected orders as Delivered"

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Inventory)