"""pytest-django fixtures."""

import pytest
from rest_framework.test import APIClient

from accounts.models import Address, Cat, User
from catalog.models import Brand, Category, Product, Tag


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="password123", full_name="Test User")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="password123")


@pytest.fixture
def auth_client(api_client, user):
    """APIClient with a valid JWT for `user` already set."""
    resp = api_client.post(
        "/api/v1/auth/login/",
        {"email": "user@example.com", "password": "password123"},
        format="json",
    )
    token = resp.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def catalog_data(db):
    """A small but realistic catalog: 2 brands, 2 categories, 3 tags, 3 products."""
    rc = Brand.objects.create(name="Royal Canin")
    whiskas = Brand.objects.create(name="Whiskas")
    dry = Category.objects.create(name="Dry Food")
    wet = Category.objects.create(name="Wet Food")
    chicken = Tag.objects.create(name="chicken")
    fish = Tag.objects.create(name="fish")
    grain_free = Tag.objects.create(name="grain-free")

    kitten_dry = Product.objects.create(
        name="Kitten Dry 2kg",
        brand=rc,
        category=dry,
        price_cents=2499,
        stock_qty=20,
        weight_grams=2000,
        life_stage_target="kitten",
    )
    kitten_dry.tags.add(chicken)

    senior_dry = Product.objects.create(
        name="Senior 7+ 2kg",
        brand=rc,
        category=dry,
        price_cents=2990,
        stock_qty=10,
        weight_grams=2000,
        life_stage_target="senior",
    )
    senior_dry.tags.add(chicken)

    wet_pouch = Product.objects.create(
        name="Fish Pouches 12x",
        brand=whiskas,
        category=wet,
        price_cents=1890,
        stock_qty=50,
        weight_grams=840,
        life_stage_target="all",
    )
    wet_pouch.tags.add(fish, grain_free)

    return {
        "brands": {"rc": rc, "whiskas": whiskas},
        "categories": {"dry": dry, "wet": wet},
        "tags": {"chicken": chicken, "fish": fish, "grain_free": grain_free},
        "products": {"kitten_dry": kitten_dry, "senior_dry": senior_dry, "wet_pouch": wet_pouch},
    }


@pytest.fixture
def user_cat(user):
    return Cat.objects.create(owner=user, name="Whiskers", life_stage="senior")


@pytest.fixture
def user_address(user):
    return Address.objects.create(
        owner=user,
        recipient_name="Nafisa Islam",
        line1="Straße 1",
        postal_code="09126",
        city="Chemnitz",
        country="Germany",
        is_default=True,
    )
