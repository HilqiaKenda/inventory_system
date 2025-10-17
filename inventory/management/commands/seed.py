from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from decimal import Decimal
from inventory.models import (
    Category,
    Supplier,
    Product,
    ProductSupplier,
    Inventory,
    Cart,
    CartItem,
    Order,
    OrderItem,
)

fake = Faker()


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        self.create_users(10)
        self.create_categories(10)
        self.create_suppliers(10)
        self.create_products(20)
        self.create_product_suppliers()
        self.create_inventories()
        self.create_carts_and_items()
        self.create_orders(15)
        self.create_order_items()

        self.stdout.write(self.style.SUCCESS("✅ Done seeding database!"))

    def create_users(self, total):
        for _ in range(total):
            username = fake.unique.user_name()
            email = fake.unique.email()
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, email=email, password="password123"
                )
                user.first_name = fake.first_name()
                user.last_name = fake.last_name()
                user.save()
                # create a cart for each user
                Cart.objects.get_or_create(user=user)

    def create_categories(self, total):
        for _ in range(total):
            Category.objects.get_or_create(
                name=fake.unique.word().title(),
                defaults={"description": fake.text(max_nb_chars=100)},
            )

    def create_suppliers(self, total):
        for _ in range(total):
            Supplier.objects.get_or_create(
                email=fake.unique.company_email(),
                defaults={
                    "name": fake.company(),
                    "phone": fake.msisdn()[:15],
                    "address": fake.address(),
                },
            )

    def create_products(self, total):
        categories = list(Category.objects.all())
        for _ in range(total):
            Product.objects.get_or_create(
                name=fake.unique.word().title(),
                defaults={
                    "category": random.choice(categories),
                    "description": fake.text(max_nb_chars=200),
                    "price": round(Decimal(random.uniform(5, 500)), 2),
                    "sku": fake.unique.uuid4()[:12],
                    "is_active": random.choice([True, True, True, False]),
                },
            )

    def create_product_suppliers(self):
        products = list(Product.objects.all())
        suppliers = list(Supplier.objects.all())
        for product in products:
            for supplier in random.sample(suppliers, random.randint(1, 3)):
                ProductSupplier.objects.get_or_create(
                    product=product,
                    supplier=supplier,
                    defaults={
                        "supplier_price": round(Decimal(random.uniform(3, 400)), 2),
                        "is_primary": random.choice([True, False]),
                    },
                )

    def create_inventories(self):
        for product in Product.objects.all():
            Inventory.objects.get_or_create(
                product=product,
                defaults={
                    "quantity": random.randint(0, 200),
                    "reserved_quantity": random.randint(0, 20),
                    "reorder_level": random.randint(5, 20),
                },
            )

    def create_carts_and_items(self):
        users = User.objects.all()
        products = list(Product.objects.all())
        for user in users:
            cart, _ = Cart.objects.get_or_create(user=user)
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": random.randint(1, 5)},
                )

    def create_orders(self, total):
        users = list(User.objects.all())
        for _ in range(total):
            user = random.choice(users)
            Order.objects.create(
                user=user,
                status=random.choice([s[0] for s in Order.STATUS_CHOICES]),
                shipping_address=fake.address(),
                shipping_phone=fake.msisdn()[:15],
                subtotal=0,
                shipping_cost=round(Decimal(random.uniform(5, 20)), 2),
                tax_amount=round(Decimal(random.uniform(2, 10)), 2),
                total_amount=0,
                notes=fake.text(max_nb_chars=50),
            )

    def create_order_items(self):
        products = list(Product.objects.all())
        for order in Order.objects.all():
            subtotal = Decimal("0.00")
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                qty = random.randint(1, 5)
                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=product.price,
                )
                subtotal += item.total_price
            order.subtotal = subtotal
            order.total_amount = subtotal + order.shipping_cost + order.tax_amount
            order.save()
