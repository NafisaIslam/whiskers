"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def health(_request):
    from django.http import JsonResponse

    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    # OpenAPI / docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # app routers
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include("catalog.urls")),
    path("api/v1/", include("orders.urls")),
]
