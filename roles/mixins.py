from django.conf import settings
import re
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.contrib import messages
from roles.helpers import has_required_permissions


def to_snake_case(value):
    # Replace spaces with underscores first
    value = value.replace(" ", "_")
    # Add underscore before capital letters (but not at the start)
    value = re.sub(r'(?<!^)(?=[A-Z])', '_', value)
    # Replace multiple underscores with a single one
    value = re.sub(r'_+', '_', value)
    return value.lower()



class AutoPermissionMixin:

    @classmethod
    def create_default_permissions(cls):
        meta = getattr(cls, '_meta', None)

        # Determine code label
        label_source = getattr(meta, 'verbose_name', None) or cls.__name__
        code_base = to_snake_case(label_source)

        # Human-readable name
        display_name = getattr(meta, 'verbose_name', cls.__name__).title()

        content_type = ContentType.objects.get_for_model(cls)

        # Decide which permissions to use
        if hasattr(cls, "override_permissions") and callable(cls.override_permissions):
            # Only use override list
            perm_names = cls.override_permissions()
        else:
            # Default + extras
            perm_names = ["Read", "Write"]
            if hasattr(cls, "extra_permissions") and callable(cls.extra_permissions):
                perm_names.extend(cls.extra_permissions())

        from .models import CustomPermission
        # if available_permissions.exists():
        #     settings.LOGGER.info(f"Permissions for {cls.__name__} already exist.")
        #     return
        for action in perm_names:
            action_code = to_snake_case(action)
            if action == "Write":
                action = "create or update"
            CustomPermission.objects.get_or_create(
                code=f"{action_code}_{code_base}",
                defaults={
                    "content_type": content_type,
                    "name": f"{action} {display_name}",
                    "description": f"Users with this role can {action.lower()} {display_name}",
                    "is_active": True
                }
            )
            settings.LOGGER.info(f"Permission {action.lower()}_{code_base} created for {cls.__name__}")
            
# ===== Mixin for Class-Based Views =====
class RequiredPermissionMixin:
    def required_permissions(self):
        """Override this in CBVs to return required permission codes."""
        return []

    def dispatch(self, request, *args, **kwargs):
        codes = self.required_permissions()
        if not has_required_permissions(request.user, codes):
            messages.warning(request, "You do not have access to this page.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        return super().dispatch(request, *args, **kwargs)
    
    
# def required_permissions(self):
#     return ["read_system_user", "read_asset_category"]