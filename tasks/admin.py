from django.contrib import admin
from .models import Task, TaskUpdate


class TaskUpdateInline(admin.TabularInline):
    model = TaskUpdate
    extra = 0
    readonly_fields = ('percent_contribution', 'created', 'updated')
    fields = ('date', 'submitted_by', 'value_achieved', 'actual_cost', 'notes', 'is_active', 'created')

    def percent_contribution(self, obj):
        return f"{obj.value_achieved}"
    percent_contribution.short_description = "Value"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskUpdateInline]

    list_display = (
        'name',
        'discipline',
        'assigned_to',
        'measurement_type',
        'weight',
        'budgeted_cost',
        'percent_complete',
        'planned_start',
        'planned_end',
        'is_active',
    )
    list_filter = (
        'measurement_type',
        'is_active',
        'discipline__project',
        'discipline__discipline',
    )
    search_fields = (
        'name',
        'description',
        'assigned_to__first_name',
        'assigned_to__last_name',
        'discipline__project__name',
    )
    readonly_fields = (
        'percent_complete',
        'created',
        'updated',
    )
    autocomplete_fields = ('assigned_to', 'collaborators')
    filter_horizontal = ('collaborators',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'discipline', 'is_active'),
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'collaborators'),
        }),
        ('Scheduling & Cost', {
            'fields': ('planned_start', 'planned_end', 'planned_hours', 'budgeted_cost'),
        }),
        ('Measurement', {
            'fields': ('measurement_type', 'target_value', 'unit_label', 'weight'),
        }),
        ('Computed (read-only)', {
            'fields': ('percent_complete',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )


@admin.register(TaskUpdate)
class TaskUpdateAdmin(admin.ModelAdmin):
    list_display = (
        'task',
        'date',
        'submitted_by',
        'value_achieved',
        'is_active',
        'created',
    )
    list_filter = (
        'is_active',
        'task__measurement_type',
        'task__discipline__project',
        'task__discipline__discipline',
    )
    search_fields = (
        'task__name',
        'submitted_by__first_name',
        'submitted_by__last_name',
        'notes',
    )
    readonly_fields = ('created', 'updated')
    autocomplete_fields = ('task', 'submitted_by')

    fieldsets = (
        ('Update Info', {
            'fields': ('task', 'date', 'submitted_by', 'is_active'),
        }),
        ('Values', {
            'fields': ('value_achieved', 'notes'),
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )