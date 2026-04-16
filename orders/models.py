"""Cart + Order domain.

Design note — price snapshotting: `OrderItem.unit_price_cents` copies the
product price at checkout time. When the Product's price later changes,
existing orders keep the price they were placed at. This is the correct
behaviour for any real commerce system and a good interview talking point.
"""

from django.conf import settings
from django.db import models

from catalog.models import Product


class Cart(models.Model):
    """One cart per user. Auto-created when first accessed."""

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart of {self.owner.email}"

    @property
    def subtotal_cents(self) -> int:
        return sum(item.line_total_cents for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("cart", "product")]

    def __str__(self) -> str:
        return f"{self.quantity}× {self.product.name}"

    @property
    def line_total_cents(self) -> int:
        return self.product.price_cents * self.quantity


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    subtotal_cents = models.PositiveIntegerField()
    shipping_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField()
    shipping_recipient = models.CharField(max_length=255)
    shipping_line1 = models.CharField(max_length=255)
    shipping_line2 = models.CharField(max_length=255, blank=True)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_city = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.owner.email}, {self.status})"


class OrderItem(models.Model):
    """Price snapshot — see module docstring."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)  # denormalised snapshot
    quantity = models.PositiveIntegerField()
    unit_price_cents = models.PositiveIntegerField()

    @property
    def line_total_cents(self) -> int:
        return self.unit_price_cents * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity}× {self.product_name}"
