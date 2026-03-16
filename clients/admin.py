from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'contact_person',
        'email',
        'phone',
        'is_active',
        'created',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Client Info', {
            'fields': ('name', 'contact_person', 'is_active'),
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address'),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )