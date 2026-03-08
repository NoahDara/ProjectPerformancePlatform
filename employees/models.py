from django.db import models
from helpers.models import BaseModel



class Employee(BaseModel):
    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee"
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees"
    )
    position = models.ForeignKey(
        "disciplines.Position",
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees"
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def discipline(self):
        """Infer discipline from position — never stored directly."""
        if self.position:
            return self.position.discipline
        return None