from rest_framework import serializers

from catalog.models import Brand, Category, Product, Tag


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "description")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class ProductListSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    price_eur = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "slug",
            "name",
            "brand",
            "category",
            "price_cents",
            "price_eur",
            "stock_qty",
            "weight_grams",
            "life_stage_target",
            "image_url",
            "is_active",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    price_eur = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "slug",
            "name",
            "brand",
            "category",
            "tags",
            "description",
            "price_cents",
            "price_eur",
            "stock_qty",
            "weight_grams",
            "life_stage_target",
            "image_url",
            "is_active",
            "created_at",
            "updated_at",
        )
