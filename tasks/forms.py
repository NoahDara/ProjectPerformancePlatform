from helpers.forms import CustomBaseForm
from .models import Task

class TaskForm(CustomBaseForm):
    class Meta:
        model = Task
        fields = "__all__"
        exclude = ['project', 'baseline_end_date', 'baseline_budget', 'baseline_locked', 'actual_end_date']
        