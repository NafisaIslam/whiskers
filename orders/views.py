from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Address
from catalog.models import Product

from .models import Cart, CartItem, Order
from .serializers import (
    AddToCartSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
)
from .services import CheckoutError, checkout


def _get_or_create_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(owner=user)
    return cart


class CartViewSet(viewsets.GenericViewSet):
    """Thin viewset — cart is a singleton per user, so no list/retrieve by id."""

    serializer_class = CartSerializer

    def get_cart(self) -> Cart:
        return _get_or_create_cart(self.request.user)

    def list(self, request):
        return Response(CartSerializer(self.get_cart()).data)

    @action(detail=False, methods=["post"], url_path="items")
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self.get_cart()
        product = get_object_or_404(Product, pk=serializer.validated_data["product_id"])
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": serializer.validated_data["quantity"]}
        )
        if not created:
            item.quantity += serializer.validated_data["quantity"]
            item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["patch", "delete"], url_path=r"items/(?P<item_id>\d+)")
    def modify_item(self, request, item_id=None):
        cart = self.get_cart()
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        if request.method == "DELETE":
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        quantity = request.data.get("quantity")
        if quantity is None or int(quantity) < 1:
            return Response({"detail": "quantity must be >= 1"}, status=400)
        item.quantity = int(quantity)
        item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = get_object_or_404(
            Address, pk=serializer.validated_data["address_id"], owner=request.user
        )
        cart = self.get_cart()
        try:
            order = checkout(cart, address, note=serializer.validated_data["note"])
        except CheckoutError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(owner=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )
