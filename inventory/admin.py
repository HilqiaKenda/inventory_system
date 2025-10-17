# from django.contrib import admin
# from . import models

# # Register your models here.
# # inventory/admin.py
# admin.site.site_header = "Groot Business Admin"
# admin.site.index_title = "Business Admin"


# # admin.site.register(models.Product)
# @admin.register(models.Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'formatted_price', 'price', 'product_status', 'quantity']
#     ordering = ['id', 'name', 'price', 'quantity']
#     list_editable = ['price']
    
#     @admin.display(ordering='quantity')
#     def product_status(self, status):
#         if status.quantity < 100:
#             return "LOW"
#         elif status.quantity <= 300:
#             return "GOOD TO GO"
#         else:
#             return "GOOD"
        
#     def formatted_price(sefl, prices):
#         return f"${prices.price: .2f}"
    
#     formatted_price.short_description = 'price'
    
#     @admin.display(ordering= 'quantity')
#     def  quantity_status(self, quantity):
#         if quantity < 20:
#             return "LOW"
#         else:
#             return "OK"

# @admin.register(models.Supplier)
# class supplierAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'email', 'phone')
#     list_editable = ('email', 'phone')
# @admin.register(models.Customer)
# class customerAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'email')
#     ordering = ('id', 'name')

# @admin.register(models.Inventory)
# class inventoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'product', 'quantity', 'quantity_status')
#     ordering = ('id', 'product','quantity')

#     @admin.display(ordering='quantity')
#     def quantity_status(self, status):
#         if status.quantity < 100:
#             return 'LOW'
#         elif status.quantity <= 300:
#             return "GOOD TO GO"
#         else:
#             return "GOOD"

# @admin.register(models.Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'status', 'order_date')
#     ordering = (['status'])
#     actions = ['set_status_pending', 'set_status_shipped', 'set_status_delivered']

#     def set_status_pending(self, request, queryset):
#         queryset.update(status='P')
#         self.message_user(request, "Selected orders have been marked as Pending.")
#     set_status_pending.short_description = "Mark selected orders as Pending"

#     def set_status_shipped(self, request, queryset):
#         queryset.update(status='S')
#         self.message_user(request, "Selected orders have been marked as Shipped.")
#     set_status_shipped.short_description = "Mark selected orders as Shipped"

#     def set_status_delivered(self, request, queryset):
#         queryset.update(status='D')
#         self.message_user(request, "Selected orders have been marked as Delivered.")
#     set_status_delivered.short_description = "Mark selected orders as Delivered"
