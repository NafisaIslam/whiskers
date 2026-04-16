from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import BrandViewSet, CategoryViewSet, ProductViewSet, TagViewSet

router = DefaultRouter()
router.register("brands", BrandViewSet, basename="brands")
router.register("categories", CategoryViewSet, basename="categories")
router.register("tags", TagViewSet, basename="tags")
router.register("products", ProductViewSet, basename="products")

urlpatterns = [path("", include(router.urls))]
