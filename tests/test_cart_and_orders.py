import pytest

from catalog.models import Product

pytestmark = pytest.mark.django_db


def test_empty_cart_auto_created(auth_client):
    resp = auth_client.get("/api/v1/cart/")
    assert resp.status_code == 200
    assert resp.data["items"] == []
    assert resp.data["subtotal_cents"] == 0


def test_add_item_to_cart(auth_client, catalog_data):
    product = catalog_data["products"]["kitten_dry"]
    resp = auth_client.post(
        "/api/v1/cart/items/", {"product_id": product.id, "quantity": 2}, format="json"
    )
    assert resp.status_code == 201
    assert resp.data["quantity"] == 2
    cart_resp = auth_client.get("/api/v1/cart/")
    assert cart_resp.data["subtotal_cents"] == product.price_cents * 2


def test_add_same_item_twice_increases_quantity(auth_client, catalog_data):
    product = catalog_data["products"]["kitten_dry"]
    auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
    auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")
    cart = auth_client.get("/api/v1/cart/").data
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 4


def test_checkout_empty_cart_fails(auth_client, user_address):
    resp = auth_client.post(
        "/api/v1/cart/checkout/", {"address_id": user_address.id}, format="json"
    )
    assert resp.status_code == 400
    assert "empty" in resp.data["detail"].lower()


def test_checkout_happy_path(auth_client, catalog_data, user_address):
    product = catalog_data["products"]["kitten_dry"]
    initial_stock = product.stock_qty
    auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")

    resp = auth_client.post(
        "/api/v1/cart/checkout/",
        {"address_id": user_address.id, "note": "Leave at door"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["status"] == "paid"
    assert resp.data["subtotal_cents"] == product.price_cents * 3
    assert resp.data["total_cents"] == product.price_cents * 3 + 499
    assert len(resp.data["items"]) == 1

    # Stock decremented, cart cleared
    product.refresh_from_db()
    assert product.stock_qty == initial_stock - 3
    cart = auth_client.get("/api/v1/cart/").data
    assert cart["items"] == []


def test_checkout_insufficient_stock(auth_client, catalog_data, user_address):
    senior = catalog_data["products"]["senior_dry"]
    auth_client.post(
        "/api/v1/cart/items/", {"product_id": senior.id, "quantity": senior.stock_qty + 5}, format="json"
    )
    resp = auth_client.post(
        "/api/v1/cart/checkout/", {"address_id": user_address.id}, format="json"
    )
    assert resp.status_code == 400
    assert "stock" in resp.data["detail"].lower()
    # Stock unchanged (atomic rollback)
    senior.refresh_from_db()
    assert senior.stock_qty > 0


def test_order_price_is_snapshotted(auth_client, catalog_data, user_address):
    product = catalog_data["products"]["kitten_dry"]
    original_price = product.price_cents
    auth_client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
    order = auth_client.post(
        "/api/v1/cart/checkout/", {"address_id": user_address.id}, format="json"
    ).data

    # Price increases after order is placed.
    Product.objects.filter(id=product.id).update(price_cents=original_price + 500)

    fresh = auth_client.get(f"/api/v1/orders/{order['id']}/").data
    assert fresh["items"][0]["unit_price_cents"] == original_price


def test_list_orders_excludes_other_users(auth_client, catalog_data, user_address, other_user):
    from accounts.models import Address as A
    from orders.models import Cart
    from orders.services import checkout as do_checkout

    # Other user places an order outside the auth_client.
    their_cart, _ = Cart.objects.get_or_create(owner=other_user)
    their_cart.items.create(product=catalog_data["products"]["wet_pouch"], quantity=1)
    their_address = A.objects.create(
        owner=other_user, recipient_name="O", line1="X", postal_code="1", city="Berlin"
    )
    do_checkout(their_cart, their_address)

    resp = auth_client.get("/api/v1/orders/")
    assert resp.status_code == 200
    assert resp.data["count"] == 0


def test_cannot_checkout_with_other_users_address(auth_client, catalog_data, other_user):
    from accounts.models import Address as A

    their_address = A.objects.create(
        owner=other_user, recipient_name="O", line1="X", postal_code="1", city="Berlin"
    )
    auth_client.post(
        "/api/v1/cart/items/",
        {"product_id": catalog_data["products"]["kitten_dry"].id, "quantity": 1},
        format="json",
    )
    resp = auth_client.post(
        "/api/v1/cart/checkout/", {"address_id": their_address.id}, format="json"
    )
    assert resp.status_code == 404
