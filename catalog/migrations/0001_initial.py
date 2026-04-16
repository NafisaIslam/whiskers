from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=120, unique=True)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "categories"},
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=60, unique=True)),
                ("slug", models.SlugField(max_length=80, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("description", models.TextField(blank=True)),
                ("price_cents", models.PositiveIntegerField(help_text="Price in euro cents")),
                ("stock_qty", models.PositiveIntegerField(default=0)),
                ("weight_grams", models.PositiveIntegerField(default=0, help_text="Package weight in grams")),
                ("life_stage_target", models.CharField(choices=[("kitten", "Kitten"), ("adult", "Adult"), ("senior", "Senior"), ("all", "All ages")], default="all", max_length=10)),
                ("image_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("brand", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.brand")),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.category")),
                ("tags", models.ManyToManyField(blank=True, related_name="products", to="catalog.tag")),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["life_stage_target"], name="catalog_pro_life_st_idx"),
                    models.Index(fields=["brand", "is_active"], name="catalog_pro_brand_a_idx"),
                ],
            },
        ),
    ]
