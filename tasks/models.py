from django.db import models
from django.core.exceptions import ValidationError
from helpers.models import BaseModel
from employees.models import Employee
from projects.models import ProjectDiscipline
from django.utils import timezone

from roles.mixins import AutoPermissionMixin

class Task(AutoPermissionMixin, BaseModel):
    MEASUREMENT_CHOICES = [
        ('percentage', 'Percentage (%)'),
        ('units', 'Units (e.g. piles, columns)'),
        ('linear', 'Linear Measure (e.g. metres)'),
        ('hours', 'Hours'),
        ('lump_sum', 'Lump Sum (Done / Not Done)'),
    ]

    discipline = models.ForeignKey(
        ProjectDiscipline,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_tasks"
    )
    collaborators = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="collaborated_tasks"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Scheduling
    planned_start = models.DateField()
    planned_end = models.DateField()
    planned_hours = models.FloatField(null=True, blank=True)
    budgeted_cost = models.FloatField()

    # Weight within its discipline — all tasks per discipline must sum to 100
    weight = models.FloatField(help_text="% weight of this task within its discipline. All tasks must sum to 100.")
    # Measurement configuration
    measurement_type = models.CharField(
        max_length=20,
        choices=MEASUREMENT_CHOICES,
        default='percentage'
    )
    target_value = models.FloatField(null=True,blank=True,
        help_text="Target quantity for units/linear/hours types. Leave blank for percentage and lump sum.")
    unit_label = models.CharField(max_length=50, blank=True, null=True,
        help_text="Label for the unit of measure e.g. 'piles', 'metres', 'hours'.")

    class Meta(BaseModel.Meta):
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.name} — {self.discipline}"

    def clean(self):
        # Assigned employee must match task discipline
        if self.assigned_to and self.assigned_to.position:
            task_discipline = self.discipline.discipline
            employee_discipline = self.assigned_to.position.discipline
            if employee_discipline != task_discipline:
                raise ValidationError(
                    f"{self.assigned_to.full_name} belongs to "
                    f"{employee_discipline} and cannot be assigned to a "
                    f"{task_discipline.name} task."
                )

        # Units/linear/hours must have a target value
        if self.measurement_type in ('units', 'linear', 'hours'):
            if not self.target_value:
                raise ValidationError(
                    f"A target value is required for "
                    f"'{self.get_measurement_type_display()}' tasks."
                )

        # Percentage and lump_sum must NOT have a target value
        if self.measurement_type in ('percentage', 'lump_sum'):
            if self.target_value:
                raise ValidationError(
                    f"Target value must be empty for "
                    f"'{self.get_measurement_type_display()}' tasks."
                )

        # Task weights must not exceed 100 within their discipline
        total = Task.objects.filter(
            discipline=self.discipline
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('weight')
        )['total'] or 0

        if total + self.weight > 100:
            raise ValidationError(
                f"Task weights cannot exceed 100% for this discipline. "
                f"Already allocated: {total}%. "
                f"Attempting to add: {self.weight}%."
            )

    @property
    def percent_complete(self):
        """
        Calculate cumulative % complete based on measurement type.
        - units / linear / hours: sum of all updates / target * 100
        - percentage: latest update value (not sum)
        - lump_sum: 100 if any update marks it done, else 0
        """
        updates = self.updates.filter(is_active=True).order_by('date')
        if not updates.exists():
            return 0

        if self.measurement_type in ('units', 'linear', 'hours'):
            total_achieved = sum(u.value_achieved for u in updates)
            if not self.target_value or self.target_value == 0:
                return 0
            return min(round((total_achieved / self.target_value) * 100, 2), 100)

        elif self.measurement_type == 'percentage':
            # Latest entry is the current cumulative %
            return updates.last().value_achieved

        elif self.measurement_type == 'lump_sum':
            return 100 if updates.filter(value_achieved=1).exists() else 0

        return 0


class TaskUpdate(BaseModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="updates"
    )
    submitted_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="submitted_updates"
    )
    date = models.DateField(default=timezone.now)
    value_achieved = models.FloatField(
        help_text=(
            "For units/linear/hours: quantity achieved THIS session (additive). "
            "For percentage: new cumulative % complete (latest wins). "
            "For lump_sum: 1 = done, 0 = not done."
        )
    )
    notes = models.TextField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Task Update"
        verbose_name_plural = "Task Updates"

    def __str__(self):
        return f"{self.task.name} — {self.date} — {self.value_achieved}"

    def clean(self):
        # Lump sum only accepts 0 or 1
        if self.task.measurement_type == 'lump_sum':
            if self.value_achieved not in (0, 1):
                raise ValidationError(
                    "Lump sum tasks only accept 0 (not done) or 1 (done)."
                )

        # Percentage must be between 0 and 100
        if self.task.measurement_type == 'percentage':
            if not (0 <= self.value_achieved <= 100):
                raise ValidationError(
                    "Percentage value must be between 0 and 100."
                )

        # Units/linear/hours must be positive
        if self.task.measurement_type in ('units', 'linear', 'hours'):
            if self.value_achieved < 0:
                raise ValidationError(
                    "Value achieved cannot be negative."
                )