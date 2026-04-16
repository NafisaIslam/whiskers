import django.contrib.auth.models
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, verbose_name="superuser status")),
                ("email", models.EmailField(db_index=True, max_length=254, unique=True, verbose_name="email address")),
                ("full_name", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("groups", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"verbose_name": "user", "verbose_name_plural": "users"},
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name="Cat",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("breed", models.CharField(blank=True, max_length=100)),
                ("birth_date", models.DateField(blank=True, null=True)),
                ("weight_kg", models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ("life_stage", models.CharField(choices=[("kitten", "Kitten"), ("adult", "Adult"), ("senior", "Senior")], default="adult", max_length=10)),
                ("allergy_notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=models.CASCADE, related_name="cats", to="accounts.user")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("recipient_name", models.CharField(max_length=255)),
                ("line1", models.CharField(max_length=255)),
                ("line2", models.CharField(blank=True, max_length=255)),
                ("postal_code", models.CharField(max_length=20)),
                ("city", models.CharField(max_length=100)),
                ("country", models.CharField(default="Germany", max_length=100)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=models.CASCADE, related_name="addresses", to="accounts.user")),
            ],
            options={"ordering": ["-is_default", "-created_at"], "verbose_name_plural": "addresses"},
        ),
    ]
