from rest_framework import serializers

from catalog.models import Product

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_price_cents = serializers.IntegerField(source="product.price_cents", read_only=True)
    line_total_cents = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_name", "quantity", "unit_price_cents", "line_total_cents")
        read_only_fields = ("id", "product_name", "unit_price_cents", "line_total_cents")


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Product not found or inactive")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal_cents = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "subtotal_cents", "created_at", "updated_at")
        read_only_fields = fields


class OrderItemSerializer(serializers.ModelSerializer):
    line_total_cents = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "unit_price_cents", "line_total_cents")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "subtotal_cents",
            "shipping_cents",
            "total_cents",
            "shipping_recipient",
            "shipping_line1",
            "shipping_line2",
            "shipping_postal_code",
            "shipping_city",
            "shipping_country",
            "note",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True, default="")
