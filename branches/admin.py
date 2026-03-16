from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'email',
        'is_active',
        'created',
        'updated',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'email')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Branch Info', {
            'fields': ('name', 'code', 'email', 'address', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )