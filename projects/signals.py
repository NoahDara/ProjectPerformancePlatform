from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, ProjectDiscipline
from disciplines.models import Discipline


@receiver(post_save, sender=Project)
def create_project_disciplines(sender, instance, created, **kwargs):
    if not created:
        return

    disciplines = Discipline.objects.filter(is_active=True, is_deleted=False)

    project_disciplines = [
        ProjectDiscipline(
            project=instance,
            discipline=discipline,
            planned_weight=0,
            budget_allocated=0,
        )
        for discipline in disciplines
    ]

    ProjectDiscipline.objects.bulk_create(project_disciplines)