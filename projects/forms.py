from helpers.forms import CustomBaseForm
from .models import Project

class ProjectForm(CustomBaseForm):
    class Meta:
        model = Project
        fields = "__all__"
        exclude = ['baseline_start_date', 'baseline_end_date', 'baseline_budget', 'baseline_locked', 'actual_end_date']
        
        
from django import forms
from .models import ProjectDiscipline
from employees.models import Employee


class ProjectDisciplineForm(forms.ModelForm):
    class Meta:
        model = ProjectDiscipline
        fields = ['manager', 'planned_weight', 'budget_allocated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            discipline = self.instance.discipline
            self.fields['manager'].queryset = Employee.objects.filter(
                position__discipline=discipline,
                is_active=True,
            )

        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(field, forms.ModelChoiceField):
                widget.attrs.update({
                    "class": "form-select js-select2",
                    "data-search": "on",
                    "data-allow-clear": "true",
                    "id": f"{name}-id",
                })
            else:
                widget.attrs.update({
                    "class": "form-control",
                    "id": f"{name}-id",
                })

        self.fields['manager'].label = "Manager"
        self.fields['planned_weight'].label = "Weight (%)"
        self.fields['budget_allocated'].label = "Budget"