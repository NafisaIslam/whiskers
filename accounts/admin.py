from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import Address, Cat, User


class CatInline(admin.TabularInline):
    model = Cat
    extra = 0
    fields = ("name", "breed", "life_stage", "weight_kg", "birth_date")


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ("recipient_name", "line1", "city", "postal_code", "country", "is_default")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "is_staff", "is_active", "date_joined")
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    readonly_fields = ("date_joined", "last_login")
    inlines = [CatInline, AddressInline]


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "life_stage", "breed", "weight_kg")
    list_filter = ("life_stage",)
    search_fields = ("name", "owner__email")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("recipient_name", "owner", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("recipient_name", "city", "owner__email")
