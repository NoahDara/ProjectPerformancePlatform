"roles/models/extra_content_types.py"

from django.db import models

from roles.mixins import AutoPermissionMixin

# Create your models here.

        
class CustomerRelationShipModule(AutoPermissionMixin, models.Model):
    class Meta:
        verbose_name = "Customer Relationship Module"
    
class HumanResourceModule(AutoPermissionMixin, models.Model):
    class Meta:
        verbose_name = "Human Resource Module"
    
class AssetManagementModule(AutoPermissionMixin, models.Model):
    class Meta:
        verbose_name = "Asset Management Module"
    
class InventoryManagementModule(AutoPermissionMixin, models.Model):
    class Meta:
        verbose_name = "Inventory Management Module"
        
    
class FinanceModule(AutoPermissionMixin, models.Model):
    class Meta:
        verbose_name = "Finance Module"