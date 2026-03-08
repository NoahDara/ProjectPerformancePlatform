from django.db import models
from helpers.models import BaseModel


class Client(BaseModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name