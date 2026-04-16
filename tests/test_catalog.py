import pytest

pytestmark = pytest.mark.django_db


def test_list_products_is_public(api_client, catalog_data):
    resp = api_client.get("/api/v1/products/")
    assert resp.status_code == 200
    assert resp.data["count"] == 3


def test_filter_products_by_life_stage(api_client, catalog_data):
    resp = api_client.get("/api/v1/products/?life_stage=senior")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["life_stage_target"] == "senior"


def test_filter_products_by_brand_slug(api_client, catalog_data):
    resp = api_client.get("/api/v1/products/?brand=royal-canin")
    assert resp.status_code == 200
    assert resp.data["count"] == 2


def test_filter_products_by_price_range(api_client, catalog_data):
    resp = api_client.get("/api/v1/products/?min_price=2000&max_price=2600")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["name"] == "Kitten Dry 2kg"


def test_search_products(api_client, catalog_data):
    resp = api_client.get("/api/v1/products/?search=pouches")
    assert resp.status_code == 200
    assert resp.data["count"] == 1


def test_recommended_requires_auth(api_client, catalog_data, user_cat):
    resp = api_client.get(f"/api/v1/products/recommended/?cat_id={user_cat.id}")
    assert resp.status_code == 401


def test_recommended_for_senior_cat(auth_client, catalog_data, user_cat):
    """Senior cat should see senior-targeted + 'all' products, not kitten-only."""
    resp = auth_client.get(f"/api/v1/products/recommended/?cat_id={user_cat.id}")
    assert resp.status_code == 200
    names = {p["name"] for p in resp.data["results"]}
    assert "Senior 7+ 2kg" in names
    assert "Fish Pouches 12x" in names  # life_stage_target=all
    assert "Kitten Dry 2kg" not in names


def test_recommended_excludes_allergens(auth_client, catalog_data, user_cat):
    user_cat.allergy_notes = "severe fish allergy"
    user_cat.save()
    resp = auth_client.get(f"/api/v1/products/recommended/?cat_id={user_cat.id}")
    names = {p["name"] for p in resp.data["results"]}
    assert "Fish Pouches 12x" not in names


def test_recommended_rejects_other_users_cat(auth_client, other_user):
    from accounts.models import Cat

    their_cat = Cat.objects.create(owner=other_user, name="Mittens", life_stage="adult")
    resp = auth_client.get(f"/api/v1/products/recommended/?cat_id={their_cat.id}")
    assert resp.status_code == 404


def test_product_detail_includes_tags(api_client, catalog_data):
    slug = catalog_data["products"]["wet_pouch"].slug
    resp = api_client.get(f"/api/v1/products/{slug}/")
    assert resp.status_code == 200
    tag_names = {t["name"] for t in resp.data["tags"]}
    assert "fish" in tag_names
    assert "grain-free" in tag_names
