from django.db import models
from helpers.models import BaseModel


class Discipline(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Discipline"
        verbose_name_plural = "Disciplines"

    def __str__(self):
        return self.name


class Position(BaseModel):
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name="positions"
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Position"
        verbose_name_plural = "Positions"

    def __str__(self):
        return f"{self.name} — {self.discipline.name}"