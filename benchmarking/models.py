from django.db import models
from helpers.models import BaseModel
from projects.models import Project


class ProjectSnapshot(BaseModel):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="snapshot"
    )
    discipline_mix = models.CharField(
        max_length=255,
        help_text="Sorted comma-separated discipline codes e.g. 'arch,eng,qs'"
    )
    actual_duration = models.PositiveIntegerField(
        help_text="Actual project duration in days."
    )
    final_spi = models.FloatField()
    final_cpi = models.FloatField()
    team_size = models.PositiveIntegerField()
    final_cost = models.FloatField()
    budget_at_completion = models.FloatField()

    class Meta(BaseModel.Meta):
        verbose_name = "Project Snapshot"
        verbose_name_plural = "Project Snapshots"

    def __str__(self):
        return f"Snapshot — {self.project.name}"