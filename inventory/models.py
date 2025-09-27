from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    suppliers = models.ManyToManyField(
        Supplier, through="ProductSupplier", related_name="products"
    )
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        try:
            return self.inventory.quantity > 0
        except Inventory.DoesNotExist:
            return False


class ProductSupplier(models.Model):
    """Intermediate model for Product-Supplier many-to-many relationship"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    supplier_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "supplier")

    def __str__(self):
        return f"{self.product.name} - {self.supplier.name}"


class Inventory(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="inventory"
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.product.name} - {self.available_quantity} available"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity


class UserProfile(models.Model):
    """Extended user profile for additional customer information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"
        )

    @property
    def total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    STATUS_PENDING = "P"
    STATUS_CONFIRMED = "C"
    STATUS_PROCESSING = "PR"
    STATUS_SHIPPED = "S"
    STATUS_DELIVERED = "D"
    STATUS_CANCELLED = "CA"
    STATUS_RETURNED = "R"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_RETURNED, "Returned"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="orders"
    )
    order_number = models.CharField(
        max_length=100, unique=True, editable=False, default=0
    )
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    # Shipping Information
    shipping_address = models.TextField(null=True, blank=True)
    shipping_phone = models.CharField(max_length=15, default="0xx 0xx 0xx")

    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Timestamps
    order_date = models.DateTimeField(auto_now=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notes
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username} - Status: {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid

            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Price at time of order
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.name} in Order {self.order.order_number}"
        )

    @property
    def total_price(self):
        return self.quantity * self.unit_price


# Signal to create user profile and cart automatically
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile_and_cart(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        Cart.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
    if hasattr(instance, "cart"):
        instance.cart.save()
