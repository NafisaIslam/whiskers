"""Brand, Category, Tag, Product.

Product carries cat-specific targeting (life_stage_target + dietary tags)
to power the /products/recommended endpoint.
"""

from django.db import models
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Dietary / attribute tag (grain-free, chicken, salmon, prescription...)."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    class LifeStageTarget(models.TextChoices):
        KITTEN = "kitten", "Kitten"
        ADULT = "adult", "Adult"
        SENIOR = "senior", "Senior"
        ALL = "all", "All ages"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    description = models.TextField(blank=True)
    price_cents = models.PositiveIntegerField(help_text="Price in euro cents")
    stock_qty = models.PositiveIntegerField(default=0)
    weight_grams = models.PositiveIntegerField(
        default=0, help_text="Package weight in grams"
    )
    life_stage_target = models.CharField(
        max_length=10, choices=LifeStageTarget.choices, default=LifeStageTarget.ALL
    )
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["life_stage_target"]),
            models.Index(fields=["brand", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.brand.name} — {self.name}"

    @property
    def price_eur(self) -> float:
        return self.price_cents / 100

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand_id}-{self.name}")
        super().save(*args, **kwargs)
