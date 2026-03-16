from django.contrib import admin
from .models import Discipline, Position


class PositionInline(admin.TabularInline):
    model = Position
    extra = 0
    fields = ('name', 'code', 'description', 'is_active')
    readonly_fields = ('created', 'updated')
    show_change_link = True


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    inlines = [PositionInline]

    list_display = (
        'name',
        'code',
        'position_count',
        'is_active',
        'created',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('created', 'updated', 'position_count')

    fieldsets = (
        ('Discipline Info', {
            'fields': ('name', 'code', 'description', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Positions')
    def position_count(self, obj):
        return obj.positions.count()


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'discipline',
        'is_active',
        'created',
    )
    list_filter = ('is_active', 'discipline')
    search_fields = ('name', 'code', 'discipline__name')
    readonly_fields = ('created', 'updated')
    autocomplete_fields = ('discipline',)

    fieldsets = (
        ('Position Info', {
            'fields': ('name', 'code', 'discipline', 'description', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )