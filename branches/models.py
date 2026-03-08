from django.db import models
from helpers.models import BaseModel


class Branch(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} ({self.code})"