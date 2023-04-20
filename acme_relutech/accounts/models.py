from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(
        self, email, username, password=None, is_admin=False, **extra_fields
    ):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, is_admin=is_admin, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            is_admin=True,
            **extra_fields
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_admins(self):
        return self.filter(is_admin=True)

    def get_developers(self):
        return self.filter(is_admin=False)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group, blank=True, related_name="custom_users", related_query_name="custom_user"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_users",
        related_query_name="custom_user",
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username
