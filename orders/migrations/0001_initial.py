from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cart", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("cart", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.cart")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.product")),
            ],
            options={"unique_together": {("cart", "product")}},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], db_index=True, default="pending", max_length=10)),
                ("subtotal_cents", models.PositiveIntegerField()),
                ("shipping_cents", models.PositiveIntegerField(default=0)),
                ("total_cents", models.PositiveIntegerField()),
                ("shipping_recipient", models.CharField(max_length=255)),
                ("shipping_line1", models.CharField(max_length=255)),
                ("shipping_line2", models.CharField(blank=True, max_length=255)),
                ("shipping_postal_code", models.CharField(max_length=20)),
                ("shipping_city", models.CharField(max_length=100)),
                ("shipping_country", models.CharField(max_length=100)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("product_name", models.CharField(max_length=200)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price_cents", models.PositiveIntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.product")),
            ],
        ),
    ]
