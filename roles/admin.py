from django.contrib import admin
from .models import  CustomPermission, Role
from helpers.admin import AutoExtraFieldsAdminMixin
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.


@admin.register(CustomPermission)
class CustomPermissionAdmin(AutoExtraFieldsAdminMixin, SimpleHistoryAdmin):
    list_display = ('code', 'name', 'content_type', 'is_active')
    list_filter = ('content_type', 'is_active')
    search_fields = ('code', 'name')
    ordering = ('content_type__id', 'code')

@admin.register(Role)
class RoleAdmin(AutoExtraFieldsAdminMixin, SimpleHistoryAdmin):
    list_display = ('name', 'code', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('name', 'code')
    ordering = ('name',)