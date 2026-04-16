from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import Address, Cat, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "email", "password", "full_name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "date_joined")
        read_only_fields = fields


class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = (
            "id",
            "name",
            "breed",
            "birth_date",
            "weight_kg",
            "life_stage",
            "allergy_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "recipient_name",
            "line1",
            "line2",
            "postal_code",
            "city",
            "country",
            "is_default",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
