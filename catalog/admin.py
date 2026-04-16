from django.contrib import admin
from django.utils.html import format_html

from catalog.models import Brand, Category, Product, Tag


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "price_display",
        "stock_display",
        "life_stage_target",
        "is_active",
    )
    list_filter = ("is_active", "life_stage_target", "brand", "category")
    list_editable = ("is_active",)
    search_fields = ("name", "description", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tags",)
    list_select_related = ("brand", "category")
    actions = ["mark_active", "mark_inactive"]
    fieldsets = (
        (None, {"fields": ("name", "slug", "brand", "category", "tags")}),
        ("Content", {"fields": ("description", "image_url")}),
        ("Commerce", {"fields": ("price_cents", "stock_qty", "weight_grams", "is_active")}),
        ("Targeting", {"fields": ("life_stage_target",)}),
    )
    readonly_fields: tuple = ()

    @admin.display(description="Price", ordering="price_cents")
    def price_display(self, obj):
        return f"€ {obj.price_cents / 100:.2f}"

    @admin.display(description="Stock", ordering="stock_qty")
    def stock_display(self, obj):
        if obj.stock_qty == 0:
            color = "red"
            label = "out of stock"
        elif obj.stock_qty < 10:
            color = "orange"
            label = f"{obj.stock_qty} (low)"
        else:
            color = "green"
            label = str(obj.stock_qty)
        return format_html('<b style="color:{}">{}</b>', color, label)

    @admin.action(description="Mark selected products as active")
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected products as inactive")
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
