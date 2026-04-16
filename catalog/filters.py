import django_filters

from catalog.models import Product


class ProductFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand__slug")
    category = django_filters.CharFilter(field_name="category__slug")
    tag = django_filters.CharFilter(field_name="tags__slug")
    life_stage = django_filters.CharFilter(field_name="life_stage_target")
    min_price = django_filters.NumberFilter(field_name="price_cents", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price_cents", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["brand", "category", "tag", "life_stage", "min_price", "max_price", "in_stock"]

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock_qty__gt=0)
        if value is False:
            return queryset.filter(stock_qty=0)
        return queryset
