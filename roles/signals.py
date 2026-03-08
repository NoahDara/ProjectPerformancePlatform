from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from django.apps import apps
from employees.models import Employee
from roles.mixins import AutoPermissionMixin
from .models import CustomPermission
from .models import Role
from django.contrib.auth import get_user_model
from django.conf import settings

@receiver(post_save, sender=get_user_model())
def create_admin_role(sender, instance, created, **kwargs):
    if created:
        # Create or get the admin role
        admin_role = Role.objects.filter(is_admin=True).first()
        if not admin_role:
            admin_role = Role.objects.create(name='System Administrator', code='admin', is_admin=True)

            all_permissions = CustomPermission.objects.all()
            admin_role.permissions.set(all_permissions)    

            instance.role = admin_role
            instance.save()
        
# Global flag to prevent multiple runs
_permissions_created = False

@receiver(post_migrate)
def create_model_permissions(sender, **kwargs):
    global _permissions_created
    if _permissions_created:
        return  # Already ran once; skip

    for model in apps.get_models():
        if issubclass(model, AutoPermissionMixin) and not model._meta.abstract:
            model.create_default_permissions()
    admin_roles = Role.objects.filter(is_admin=True).all()
    all_permissions = CustomPermission.objects.all()
    for role in admin_roles:
        role.permissions.set(all_permissions)  
        role.save()
    _permissions_created = True 