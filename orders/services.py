"""Checkout service: cart -> order.

Kept in a dedicated module (not in a view) so it is unit-testable and
easy to call from other contexts (admin actions, future background jobs).
"""

from __future__ import annotations

from django.db import transaction

from accounts.models import Address
from catalog.models import Product

from .models import Cart, Order, OrderItem


class CheckoutError(Exception):
    """Raised when a checkout cannot proceed (empty cart, insufficient stock, etc.)."""


FLAT_SHIPPING_CENTS = 499  # €4.99 flat shipping for the demo


@transaction.atomic
def checkout(cart: Cart, address: Address, note: str = "") -> Order:
    """Convert a Cart into a paid Order, decrementing stock.

    Runs inside a DB transaction so a stock race (two buyers, last item)
    leaves the DB consistent. `select_for_update()` locks product rows
    for the duration.
    """
    items = list(cart.items.select_related("product"))
    if not items:
        raise CheckoutError("Cart is empty")

    product_ids = [item.product_id for item in items]
    locked_products = {
        p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    subtotal = 0
    for item in items:
        product = locked_products[item.product_id]
        if product.stock_qty < item.quantity:
            raise CheckoutError(
                f"Insufficient stock for {product.name}: have {product.stock_qty}, need {item.quantity}"
            )
        subtotal += product.price_cents * item.quantity

    shipping = FLAT_SHIPPING_CENTS
    total = subtotal + shipping

    order = Order.objects.create(
        owner=cart.owner,
        status=Order.Status.PAID,  # Demo skips payment step.
        subtotal_cents=subtotal,
        shipping_cents=shipping,
        total_cents=total,
        shipping_recipient=address.recipient_name,
        shipping_line1=address.line1,
        shipping_line2=address.line2,
        shipping_postal_code=address.postal_code,
        shipping_city=address.city,
        shipping_country=address.country,
        note=note,
    )
    for item in items:
        product = locked_products[item.product_id]
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=item.quantity,
            unit_price_cents=product.price_cents,
        )
        product.stock_qty -= item.quantity
        product.save(update_fields=["stock_qty"])

    cart.items.all().delete()
    return order
