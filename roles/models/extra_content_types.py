"roles/models/extra_content_types.py"

from django.db import models

from roles.mixins import AutoPermissionMixin

# Create your models here.

    
class HumanResourceModule(AutoPermissionMixin, models.Model):
    class Meta:
        verbose_name = "Human Resource Module"
