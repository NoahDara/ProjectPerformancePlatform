from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'phone',
        'branch',
        'position',
        'get_discipline',
        'user',
        'is_active',
        'created',
    )
    list_filter = (
        'is_active',
        'branch',
        'position__discipline',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone',
        'position__title',
        'branch__name',
    )
    readonly_fields = (
        'full_name',
        'get_discipline',
        'created',
        'updated',
    )
    autocomplete_fields = ('user', 'branch', 'position')

    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('Organisation', {
            'fields': ('branch', 'position', 'get_discipline'),
        }),
        ('Account', {
            'fields': ('user', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Discipline')
    def get_discipline(self, obj):
        return obj.discipline or '—'