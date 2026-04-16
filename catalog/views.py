from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Cat
from catalog.filters import ProductFilter
from catalog.models import Brand, Category, Product, Tag
from catalog.serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    TagSerializer,
)


class BrandViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Public catalog. Writes go through Django admin, not the API."""

    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related("tags")
    )
    permission_classes = [permissions.AllowAny]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "brand__name", "category__name"]
    ordering_fields = ["name", "price_cents", "created_at"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="recommended",
        permission_classes=[permissions.IsAuthenticated],
    )
    def recommended(self, request):
        """Products tailored to one of the caller's cats.

        Query params:
          cat_id (required): id of a Cat belonging to the current user

        Logic:
          - Filter to active products.
          - Match products whose life_stage_target is the cat's life_stage OR 'all'.
          - Exclude products whose tag names appear (case-insensitive) in the
            cat's allergy_notes.
        """
        cat_id = request.query_params.get("cat_id")
        if not cat_id:
            return Response({"detail": "cat_id query param is required"}, status=400)
        cat = get_object_or_404(Cat, pk=cat_id, owner=request.user)

        qs = self.get_queryset().filter(
            Q(life_stage_target=cat.life_stage) | Q(life_stage_target="all")
        )
        if cat.allergy_notes.strip():
            allergy_terms = [
                term.strip().lower()
                for term in cat.allergy_notes.replace(",", " ").split()
                if len(term.strip()) >= 3
            ]
            if allergy_terms:
                qs = qs.exclude(tags__name__iregex=r"(" + "|".join(allergy_terms) + ")")

        qs = qs.distinct().order_by("-stock_qty", "name")[:20]
        serializer = ProductListSerializer(qs, many=True, context={"request": request})
        return Response(
            {
                "cat": {
                    "id": cat.id,
                    "name": cat.name,
                    "life_stage": cat.life_stage,
                    "allergy_notes": cat.allergy_notes,
                },
                "results": serializer.data,
            }
        )
