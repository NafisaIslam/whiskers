import pytest

pytestmark = pytest.mark.django_db


def test_register_creates_user(api_client):
    resp = api_client.post(
        "/api/v1/auth/register/",
        {"email": "new@example.com", "password": "strong-pass-123", "full_name": "New"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["email"] == "new@example.com"


def test_register_weak_password_rejected(api_client):
    resp = api_client.post(
        "/api/v1/auth/register/",
        {"email": "weak@example.com", "password": "abc"},
        format="json",
    )
    assert resp.status_code == 400


def test_login_returns_tokens(api_client, user):
    resp = api_client.post(
        "/api/v1/auth/login/",
        {"email": "user@example.com", "password": "password123"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


def test_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/auth/me/")
    assert resp.status_code == 401


def test_me_returns_user(auth_client):
    resp = auth_client.get("/api/v1/auth/me/")
    assert resp.status_code == 200
    assert resp.data["email"] == "user@example.com"


def test_create_cat(auth_client):
    resp = auth_client.post(
        "/api/v1/auth/cats/",
        {"name": "Whiskers", "life_stage": "senior", "weight_kg": "4.20"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["name"] == "Whiskers"


def test_cannot_see_other_users_cats(auth_client, other_user):
    from accounts.models import Cat

    Cat.objects.create(owner=other_user, name="Mittens", life_stage="adult")
    resp = auth_client.get("/api/v1/auth/cats/")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 0
