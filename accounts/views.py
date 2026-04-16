from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Address, Cat
from accounts.serializers import (
    AddressSerializer,
    CatSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """GET /auth/me — current user profile."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CatViewSet(viewsets.ModelViewSet):
    serializer_class = CatSerializer

    def get_queryset(self):
        return Cat.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
