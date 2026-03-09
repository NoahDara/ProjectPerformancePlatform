from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    role = models.ForeignKey('roles.Role', on_delete=models.SET_NULL, null=True,  blank=True, related_name='users')
    is_deleted = models.BooleanField(default=False)