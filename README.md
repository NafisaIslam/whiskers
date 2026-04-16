# Whiskers — Cat Food Shop API

A REST API for a cat-food e-commerce backend. Built with Django + Django REST Framework as a portfolio project.

> **Live demo:** `<add Railway/Fly.io URL after deployment>` · Swagger UI at `/api/docs/` · Admin panel at `/admin/`.

## Why this project

Most junior portfolios have a generic "store API." This one has a niche domain (cat food) and a twist: users can register their **cats** (name, life stage, allergies) and get **personalised product recommendations** — active products whose `life_stage_target` matches the cat and whose dietary tags don't conflict with the cat's allergies. That endpoint is the interview talking point. Everything else is the scaffolding that makes it a real backend.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Web framework | **Django 5 + DRF** | Industry standard for Python web in Germany; batteries-included admin |
| ORM | **Django ORM** | Mature, tight integration with the admin |
| Database | **PostgreSQL 16** | Real DB (not SQLite); matches production |
| Auth | **djangorestframework-simplejwt** | JWT access + refresh, refresh-token rotation enabled |
| API docs | **drf-spectacular** | Auto-generated OpenAPI + Swagger UI |
| Filtering | **django-filter + DRF SearchFilter** | Standard, declarative |
| Tests | **pytest-django** | Cleaner than Django's default runner |
| Tooling | **uv + Ruff** | Fast modern Python tooling |
| Container | **Docker (multi-stage)** | Small runtime image, reproducible |
| CI | **GitHub Actions** | Lint + tests on every push against real Postgres |

## What's in it

**3 Django apps**:
- `accounts` — custom User (email login from day 1), Cat, Address
- `catalog` — Brand, Category, Tag, Product; filtering, search, `/products/recommended` personalised endpoint
- `orders` — Cart, CartItem, Order, OrderItem; transactional checkout with stock lock and price snapshotting

**~21 tests** covering auth, catalog filtering, recommendations (incl. allergy exclusion), cart operations, checkout happy path, insufficient stock, price snapshotting, and multi-tenant isolation.

**Django admin panel** — fully customised, this is half the point of using Django:
- Product list with coloured stock-level badges (red/orange/green) and inline editing of `is_active`
- Order list with status badges (pending/paid/shipped/…) and bulk actions to ship/deliver/cancel
- Inline OrderItems on each Order, Cat and Address inlines on each User
- Bulk actions (mark active/inactive, ship orders, etc.)

## Architecture highlights

### Personalised recommendation logic
`GET /api/v1/products/recommended/?cat_id=<id>` (authenticated)
1. Load the caller's Cat (ownership-checked via 404-not-403).
2. Filter active products where `life_stage_target == cat.life_stage OR 'all'`.
3. Parse the cat's `allergy_notes` into search terms; exclude products whose tags match those terms.
4. Return top 20 by stock then name.

### Transactional checkout
`orders.services.checkout()` runs inside `@transaction.atomic`, locks product rows with `SELECT ... FOR UPDATE` to prevent race conditions, validates stock, writes the Order with snapshotted prices into `OrderItem.unit_price_cents`, decrements stock, clears the cart — all or nothing. Tested against "insufficient stock" and "price changes after checkout" scenarios.

### Custom User on day 1
`AUTH_USER_MODEL = "accounts.User"` configured before the first migration. Email is the login field; username is removed. Retrofitting this after the fact in Django is painful and every Django interviewer asks about it.

## Local setup

Prerequisites: **Python 3.12+**, **Docker**, [**uv**](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```bash
# 1. Install dependencies
uv sync

# 2. Start Postgres (uses port 5433 to avoid clashing with project1-fastapi)
docker compose up -d postgres

# 3. Apply migrations
export DATABASE_URL=postgres://postgres:postgres@localhost:5433/whiskers
export DJANGO_SECRET_KEY=dev-secret
export JWT_SIGNING_KEY=dev-jwt-signing-key-at-least-32-bytes-long
uv run python manage.py migrate

# 4. Seed everything in one go (catalog + admin + demo user + cart + orders)
uv run python manage.py seed_demo

# 5. Run the dev server
uv run python manage.py runserver

# Open:
#   http://localhost:8000/admin/      Django admin panel (admin@whiskers.test / adminpass)
#   http://localhost:8000/api/docs/   Swagger UI       (demo@whiskers.test  / password123)
```

Or run everything with one command:
```bash
docker compose up --build
```
(The API container runs migrations on startup. Browse to http://localhost:8001 — compose maps port 8001 so the FastAPI project can keep 8000.)

## Demo data & local exploration

The `seed_demo` management command sets up a realistic demo environment so both the admin panel and the API have meaningful content.

**Creates:**
- Admin superuser: `admin@whiskers.test` / `adminpass` (for `/admin/`)
- Demo user: `demo@whiskers.test` / `password123` (for the API)
- 12 cat-food products across 5 brands, 5 categories, 13 dietary tags
- 2 cats for demo user: **Luna** (senior, fish allergy) and **Miso** (kitten)
- 1 address in Chemnitz
- Cart with 2 Luna-safe items ready for checkout
- 2 already-placed orders (1 PAID, 1 SHIPPED) so order status badges are visible in admin

Idempotent — safe to re-run.

**Try the admin panel first** (http://localhost:8000/admin/ as `admin@whiskers.test` / `adminpass`):
- **Products** — coloured stock badges (green/orange/red), inline "Active" toggles, filter sidebar by brand/life-stage/category.
- **Orders** — coloured status badges (PAID/SHIPPED), bulk "Mark as shipped/delivered/cancelled" actions.
- **Users → demo@whiskers.test** — Cats and Addresses inlined on the user edit page.

**Try the API** (http://localhost:8000/api/docs/, login as `demo@whiskers.test` / `password123`):
- `GET /api/v1/products/?life_stage=senior&in_stock=true` — catalog filtering.
- `GET /api/v1/auth/cats/` — note Luna's `id`.
- `GET /api/v1/products/recommended/?cat_id=<Luna's id>` — **the signature endpoint**: returns products matching Luna's life stage while excluding fish-based products because of her allergy.

See `../HOW_TO_TEST.md` at the workspace root for full walkthrough and troubleshooting.

## Tests

```bash
# Create the test DB once:
docker exec whiskers-postgres psql -U postgres -c 'CREATE DATABASE whiskers_test;'

DATABASE_URL=postgres://postgres:postgres@localhost:5433/whiskers_test \
  DJANGO_SECRET_KEY=test-secret \
  JWT_SIGNING_KEY=test-jwt-key-at-least-32-bytes-long \
  uv run pytest -v
# Expect: 26 passed
```

## API tour

```bash
# Register + log in
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"password123"}' > /dev/null
  curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
    -H 'Content-Type: application/json' \
    -d '{"email":"me@example.com","password":"password123"}' | jq -r .access)

# Browse the public catalog (no auth required)
curl http://localhost:8000/api/v1/products/?life_stage=senior

# Register a cat
curl -X POST http://localhost:8000/api/v1/auth/cats/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Whiskers","life_stage":"senior","allergy_notes":"fish allergy"}'

# Get personalised recommendations
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/products/recommended/?cat_id=1"
```

## Design choices worth defending

- **Custom User with email login from day 1** — avoids the well-known Django trap of needing to swap auth models mid-project.
- **Price snapshotted into OrderItem** — orders are immutable to later catalog price changes. Standard commerce practice.
- **`select_for_update()` in checkout** — pessimistic row lock so two concurrent buyers can't oversell the last unit.
- **CRUD on Products via Django admin, not the API** — reduces API attack surface; admin is what staff actually use.
- **Thin viewsets, services module for checkout** — makes checkout unit-testable and callable outside HTTP (cron, admin action, etc.).
- **django-filter + SearchFilter** — declarative filtering with zero custom query code.
- **Refresh token rotation** — `ROTATE_REFRESH_TOKENS=True` reduces the impact of a leaked refresh token.

## What I would build next

- **Image uploads** to S3 / Cloudflare R2 (currently just a URL field).
- **Subscription orders** (auto-reorder every N weeks — a real use-case for pet food).
- **Payment integration** (Stripe).
- **Email notifications** on order status change (Celery + Redis).
- **A RAG-powered product chatbot** — planned as a separate Project #3.

## Repo layout

```
whiskers/                Django project config (settings, urls, wsgi, asgi)
accounts/                User, Cat, Address
catalog/                 Brand, Category, Tag, Product + /products/recommended
orders/                  Cart, Order, transactional checkout
tests/                   pytest-django test suite
```

---

Built by [Nafisa Islam](https://www.linkedin.com/in/nafisaislamtuc/) · M.Sc. Web Engineering, TU Chemnitz · Open to Junior Python Backend roles in Germany.
