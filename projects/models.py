from django.db import models
from django.core.exceptions import ValidationError
from helpers.models import BaseModel
from clients.models import Client
from employees.models import Employee


class Project(BaseModel):
    PROJECT_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('infrastructure', 'Infrastructure'),
        ('industrial', 'Industrial'),
    ]
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
    ]

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects"
    )
    project_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_projects"
    )
    deputy_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deputy_projects"
    )
    name = models.CharField(max_length=255)
    project_number = models.CharField(max_length=50, unique=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')

    # Baseline fields — locked at project start, never updated
    baseline_start_date = models.DateField()
    baseline_end_date = models.DateField()
    baseline_budget = models.DecimalField(max_digits=12, decimal_places=2)
    baseline_locked = models.BooleanField(default=False)

    # Current/live fields — updated as project evolves
    start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta(BaseModel.Meta):
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.project_number} — {self.name}"

    def clean(self):
        if self.project_manager and self.deputy_manager:
            if self.project_manager == self.deputy_manager:
                raise ValidationError(
                    "Project Manager and Deputy Manager cannot be the same employee."
                )

    def lock_baseline(self):
        """
        Call this once when the project moves from Planning to Active.
        Copies current dates and budget into baseline fields and locks them.
        """
        if not self.baseline_locked:
            self.baseline_start_date = self.start_date
            self.baseline_end_date = self.planned_end_date
            self.baseline_budget = self.budget
            self.baseline_locked = True
            self.save()


class ProjectDiscipline(BaseModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="disciplines"
    )
    discipline = models.ForeignKey(
        "disciplines.Discipline",
        on_delete=models.CASCADE,
        related_name="project_disciplines"
    )
    lead = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_disciplines"
    )
    planned_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Weight of this discipline as % of total project. All disciplines must sum to 100."
    )
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta(BaseModel.Meta):
        verbose_name = "Project Discipline"
        verbose_name_plural = "Project Disciplines"
        unique_together = ('project', 'discipline')

    def __str__(self):
        return f"{self.discipline.name} — {self.project.name}"

    def clean(self):
        # Lead must belong to this discipline
        if self.lead and self.lead.position:
            if self.lead.position.discipline != self.discipline:
                raise ValidationError(
                    f"{self.lead.full_name} belongs to "
                    f"{self.lead.discipline} and cannot lead "
                    f"{self.discipline.name} on this project."
                )

        # Weights must not exceed 100 across all disciplines on this project
        total = ProjectDiscipline.objects.filter(
            project=self.project
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('planned_weight')
        )['total'] or 0

        if total + self.planned_weight > 100:
            raise ValidationError(
                f"Discipline weights cannot exceed 100%. "
                f"Already allocated: {total}%. "
                f"Attempting to add: {self.planned_weight}%."
            )

    @property
    def percent_complete(self):
        """
        Weighted average of all task percent_complete values
        within this discipline.
        """
        tasks = self.tasks.filter(is_active=True)
        if not tasks.exists():
            return 0
        total = sum(
            (t.weight * t.percent_complete) for t in tasks
        )
        return round(total / 100, 2)