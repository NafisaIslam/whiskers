"""User, Cat, Address models.

Custom user with email login is set up on day 1 (AUTH_USER_MODEL in settings).
Retrofitting this later in a Django project is painful — so we do it now.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return self.email


class Cat(models.Model):
    """A user's cat. Powers personalised product recommendations."""

    class LifeStage(models.TextChoices):
        KITTEN = "kitten", "Kitten"
        ADULT = "adult", "Adult"
        SENIOR = "senior", "Senior"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cats")
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    life_stage = models.CharField(
        max_length=10, choices=LifeStage.choices, default=LifeStage.ADULT
    )
    allergy_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner.email})"


class Address(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    recipient_name = models.CharField(max_length=255)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Germany")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name_plural = "addresses"

    def __str__(self) -> str:
        return f"{self.recipient_name}, {self.city}"
