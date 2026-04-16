from django.contrib import admin
from django.utils.html import format_html

from .models import Cart, CartItem, Order, OrderItem

STATUS_COLORS = {
    "pending": "#999999",
    "paid": "#2c7be5",
    "shipped": "#00a86b",
    "delivered": "#1f883d",
    "cancelled": "#d73a49",
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "quantity", "unit_price_cents", "line_total")
    can_delete = False

    @admin.display(description="Line total")
    def line_total(self, obj):
        return f"€ {obj.line_total_cents / 100:.2f}"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "item_count", "subtotal_display", "updated_at")
    inlines = [CartItemInline]

    @admin.display(description="# Items")
    def item_count(self, obj):
        return obj.items.count()

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return f"€ {obj.subtotal_cents / 100:.2f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "status_badge",
        "total_display",
        "shipping_city",
        "created_at",
    )
    list_filter = ("status", "shipping_country", "created_at")
    search_fields = ("owner__email", "shipping_recipient", "shipping_city")
    inlines = [OrderItemInline]
    readonly_fields = (
        "subtotal_cents",
        "shipping_cents",
        "total_cents",
        "created_at",
        "updated_at",
    )
    actions = ["mark_shipped", "mark_delivered", "mark_cancelled"]

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#666")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:10px;'
            'font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_status_display().upper(),
        )

    @admin.display(description="Total", ordering="total_cents")
    def total_display(self, obj):
        return f"€ {obj.total_cents / 100:.2f}"

    @admin.action(description="Mark selected orders as shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders as delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)

    @admin.action(description="Cancel selected orders")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Order.Status.CANCELLED)
