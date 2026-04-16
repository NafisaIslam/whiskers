"""Seed the catalog with realistic cat-food demo data.

Run: python manage.py seed_catalog
Idempotent: safe to re-run — uses get_or_create.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Brand, Category, Product, Tag


class Command(BaseCommand):
    help = "Seed the catalog with demo cat-food data"

    @transaction.atomic
    def handle(self, *args, **options):
        brands_data = [
            ("Royal Canin", "Veterinary-aligned French brand, targeted formulas."),
            ("Purina", "Mass-market brand with wide range."),
            ("Applaws", "Natural, high-meat-content wet food."),
            ("Whiskas", "Everyday brand, kid-friendly packaging."),
            ("Hill's Science Diet", "Vet-recommended, prescription lines."),
        ]
        brands = {
            name: Brand.objects.get_or_create(name=name, defaults={"description": desc})[0]
            for name, desc in brands_data
        }

        category_names = ["Dry Food", "Wet Food", "Treats", "Prescription", "Kitten Milk"]
        categories = {name: Category.objects.get_or_create(name=name)[0] for name in category_names}

        tag_names = [
            "chicken", "fish", "salmon", "tuna", "beef", "lamb", "turkey",
            "grain-free", "low-calorie", "indoor", "hairball-control",
            "sensitive-stomach", "urinary-care",
        ]
        tags = {name: Tag.objects.get_or_create(name=name)[0] for name in tag_names}

        products = [
            # (name, brand, category, price_eur, stock, weight_g, life_stage, tags)
            ("Kitten Dry 2kg", "Royal Canin", "Dry Food", 24.99, 45, 2000, "kitten", ["chicken"]),
            ("Adult Indoor 4kg", "Royal Canin", "Dry Food", 38.50, 32, 4000, "adult", ["chicken", "indoor"]),
            ("Senior 7+ 2kg", "Royal Canin", "Dry Food", 29.90, 18, 2000, "senior", ["chicken", "hairball-control"]),
            ("Urinary Care 2kg", "Royal Canin", "Prescription", 42.00, 7, 2000, "adult", ["urinary-care"]),
            ("Wet Pouches Gravy Mix 24x85g", "Whiskas", "Wet Food", 12.49, 120, 2040, "adult", ["chicken", "beef"]),
            ("Kitten Milk Replacement 400g", "Whiskas", "Kitten Milk", 9.99, 22, 400, "kitten", []),
            ("Tuna Fillet 70g (Pouches x12)", "Applaws", "Wet Food", 18.90, 65, 840, "adult", ["tuna", "fish", "grain-free"]),
            ("Salmon Fillet 70g (Pouches x12)", "Applaws", "Wet Food", 18.90, 40, 840, "adult", ["salmon", "fish", "grain-free"]),
            ("Chicken & Liver Treats 60g", "Purina", "Treats", 3.49, 200, 60, "all", ["chicken"]),
            ("Salmon Crunchies 120g", "Purina", "Treats", 4.29, 150, 120, "all", ["salmon", "fish"]),
            ("Indoor Adult Sensitive 3kg", "Hill's Science Diet", "Dry Food", 35.90, 14, 3000, "adult", ["chicken", "sensitive-stomach", "indoor"]),
            ("Low-Cal Adult 2kg", "Hill's Science Diet", "Dry Food", 32.90, 0, 2000, "adult", ["low-calorie"]),
        ]

        created_count = 0
        for name, brand_name, cat_name, price_eur, stock, weight, stage, tag_list in products:
            product, created = Product.objects.get_or_create(
                name=name,
                brand=brands[brand_name],
                defaults=dict(
                    category=categories[cat_name],
                    price_cents=int(price_eur * 100),
                    stock_qty=stock,
                    weight_grams=weight,
                    life_stage_target=stage,
                    description=f"{name} from {brand_name}.",
                ),
            )
            if created:
                created_count += 1
            product.tags.set([tags[t] for t in tag_list])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(brands)} brands, {len(categories)} categories, "
                f"{len(tags)} tags, {created_count} new products "
                f"(total products: {Product.objects.count()})."
            )
        )
