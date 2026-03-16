from django.contrib import admin
from .models import Project, ProjectDiscipline


class ProjectDisciplineInline(admin.TabularInline):
    model = ProjectDiscipline
    extra = 0
    fields = ('discipline', 'manager', 'planned_weight', 'budget_allocated', 'is_active')
    readonly_fields = ('percent_complete', 'created', 'updated')
    show_change_link = True
    autocomplete_fields = ('discipline', 'manager')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectDisciplineInline]

    list_display = (
        'project_number',
        'name',
        'project_type',
        'status',
        'branch',
        'client',
        'project_manager',
        'start_date',
        'planned_end_date',
        'baseline_locked',
        'get_budget',
        'is_active',
        'created',
    )
    list_filter = (
        'status',
        'project_type',
        'baseline_locked',
        'is_active',
        'branch',
    )
    search_fields = (
        'project_number',
        'name',
        'client__name',
        'project_manager__first_name',
        'project_manager__last_name',
        'branch__name',
    )
    readonly_fields = (
        'baseline_start_date',
        'baseline_end_date',
        'baseline_budget',
        'baseline_locked',
        'get_budget',
        'created',
        'updated',
    )
    autocomplete_fields = ('branch', 'client', 'project_manager')

    fieldsets = (
        ('Project Info', {
            'fields': (
                'project_number',
                'name',
                'project_type',
                'status',
                'is_active',
            ),
        }),
        ('Organisation', {
            'fields': ('branch', 'client', 'project_manager'),
        }),
        ('Schedule', {
            'fields': ('start_date', 'planned_end_date', 'actual_end_date'),
        }),
        ('Baseline (read-only — locked automatically on activation)', {
            'fields': (
                'baseline_locked',
                'baseline_start_date',
                'baseline_end_date',
                'baseline_budget',
            ),
            'classes': ('collapse',),
        }),
        ('Budget', {
            'fields': ('get_budget',),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Budget (computed)')
    def get_budget(self, obj):
        return f"${obj.budget:,.2f}"


@admin.register(ProjectDiscipline)
class ProjectDisciplineAdmin(admin.ModelAdmin):
    list_display = (
        'discipline',
        'project',
        'manager',
        'planned_weight',
        'budget_allocated',
        'percent_complete',
        'is_active',
        'created',
    )
    list_filter = (
        'is_active',
        'discipline',
        'project__status',
        'project__branch',
    )
    search_fields = (
        'project__name',
        'project__project_number',
        'discipline__name',
        'manager__first_name',
        'manager__last_name',
    )
    readonly_fields = (
        'percent_complete',
        'created',
        'updated',
    )
    autocomplete_fields = ('project', 'discipline', 'manager')

    fieldsets = (
        ('Discipline Assignment', {
            'fields': ('project', 'discipline', 'manager', 'is_active'),
        }),
        ('Planning', {
            'fields': ('planned_weight', 'budget_allocated'),
        }),
        ('Progress (read-only)', {
            'fields': ('percent_complete',),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )