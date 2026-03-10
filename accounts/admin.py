# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_deleted')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # Fieldsets for the EDIT user page
    fieldsets = (
        (None,               {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Custom fields'), {'fields': ('role', 'is_deleted')}),
        (_('Permissions'),   {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'),{'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for the ADD user page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_deleted'),
        }),
    )