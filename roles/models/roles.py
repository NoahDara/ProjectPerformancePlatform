# roles/models/roles.py

from django.db import models
from django.contrib.contenttypes.models import ContentType
from helpers.models import BaseModel
from roles.models.permissions import CustomPermission
    
# Create your models here.
class Role(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    permissions = models.ManyToManyField(CustomPermission, blank=True)


    def __str__(self):
        return self.name


    @property
    def total_permissions(self):
        return self.permissions.count()