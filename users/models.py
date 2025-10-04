from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""

    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MEMBER, 'Member'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete support

    class Meta:
        db_table = 'users'

    def favourite_models(self):
        """Get favourite models for this user"""
        return self.favourited_models.all()
