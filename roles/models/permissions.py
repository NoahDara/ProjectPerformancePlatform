# roles/models/permissions.py

from django.db import models
from django.contrib.contenttypes.models import ContentType
from helpers.models import BaseModel

# Create your models here.
class CustomPermission(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='custom_permissions', null=True, blank=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        ordering = ['content_type__id', 'code','updated', 'created']

    def __str__(self):
        return f"{self.name} ({self.content_type})"
    
    class Meta:
        verbose_name = "Permission"
    
    def display_name(self):
        if self.name.startswith('Write'):
            return "Write"
        elif self.name.endswith('Only'):
            return "Read"
        else:
            return self.name
        
    # @classmethod
    # def override_permissions(cls):
    #     return ["Read",]