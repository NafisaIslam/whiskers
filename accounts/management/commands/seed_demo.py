"""One command to set up a realistic demo environment.

Run: python manage.py seed_demo

Creates:
- Admin superuser: admin@whiskers.test / adminpass   (for /admin/)
- Demo user:       demo@whiskers.test  / password123 (for the API)
- Demo user's 2 cats (Luna — senior with fish allergy; Miso — kitten)
- Demo user's default address in Chemnitz
- Also runs `seed_catalog` so products/brands/tags exist
- Demo user's cart with 2 items
- 2 completed orders placed via the real checkout service (so status badges are visible in admin)

Idempotent: re-runnable. Wipes demo user's cart + orders before re-seeding those,
leaves other users alone.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Address, Cat, User
from catalog.models import Product
from orders.models import Cart, Order
from orders.services import checkout


class Command(BaseCommand):
    help = "Populate the DB with a realistic demo setup (admin + demo user + cart + orders)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("→ Running seed_catalog first...")
        call_command("seed_catalog")

        admin, admin_created = User.objects.get_or_create(
            email="admin@whiskers.test",
            defaults={"full_name": "Admin User", "is_staff": True, "is_superuser": True},
        )
        if admin_created:
            admin.set_password("adminpass")
            admin.save()

        demo, demo_created = User.objects.get_or_create(
            email="demo@whiskers.test",
            defaults={"full_name": "Demo User"},
        )
        if demo_created:
            demo.set_password("password123")
            demo.save()

        # Wipe demo's cart + orders so re-running is clean
        Cart.objects.filter(owner=demo).delete()
        Order.objects.filter(owner=demo).delete()

        luna, _ = Cat.objects.update_or_create(
            owner=demo,
            name="Luna",
            defaults={
                "breed": "British Shorthair",
                "life_stage": Cat.LifeStage.SENIOR,
                "weight_kg": 5.10,
                "allergy_notes": "fish allergy, avoid fish-based foods",
            },
        )
        miso, _ = Cat.objects.update_or_create(
            owner=demo,
            name="Miso",
            defaults={
                "breed": "Bengal",
                "life_stage": Cat.LifeStage.KITTEN,
                "weight_kg": 1.80,
                "allergy_notes": "",
            },
        )

        address, _ = Address.objects.update_or_create(
            owner=demo,
            recipient_name="Demo User",
            defaults={
                "line1": "Straße der Nationen 62",
                "postal_code": "09111",
                "city": "Chemnitz",
                "country": "Germany",
                "is_default": True,
            },
        )

        # Cart is OneToOne per user — we reuse it across the two checkouts, then
        # leave the final state with items in it for the user to explore.
        cart = Cart.objects.create(owner=demo)

        adult_or_all = Product.objects.filter(
            life_stage_target__in=["adult", "all"], stock_qty__gte=1
        ).order_by("id")
        senior_dry = Product.objects.filter(life_stage_target="senior").first()
        treats = (
            Product.objects.filter(category__name="Treats")
            .exclude(tags__name__icontains="fish")
            .first()
        )

        # Place 2 completed orders via the real checkout service
        # (each one clears the cart as a side effect)
        for idx, product in enumerate(adult_or_all[:2]):
            cart.items.create(product=product, quantity=1)
            order = checkout(cart, address, note=f"Auto-seeded demo order #{idx + 1}")
            if idx == 1:  # second order -> shipped, so the status badge varies
                order.status = Order.Status.SHIPPED
                order.save(update_fields=["status"])
            cart.refresh_from_db()

        # Leave the cart populated so /api/v1/cart/ and the admin Cart page show items
        if senior_dry:
            cart.items.create(product=senior_dry, quantity=1)
        if treats:
            cart.items.create(product=treats, quantity=2)

        self.stdout.write(
            self.style.SUCCESS(
                "\n✓ Demo environment ready.\n\n"
                "  Admin (Django /admin/):\n"
                "    email:    admin@whiskers.test\n"
                "    password: adminpass\n\n"
                "  Demo user (API):\n"
                "    email:    demo@whiskers.test\n"
                "    password: password123\n"
                "    cats:     Luna (senior, fish allergy), Miso (kitten)\n"
                "    cart:     2 items ready to checkout\n"
                "    orders:   2 placed (1 paid, 1 shipped)\n"
            )
        )
