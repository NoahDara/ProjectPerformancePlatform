from helpers.forms import CustomBaseForm
from .models import Task, TaskUpdate

class TaskForm(CustomBaseForm):
    class Meta:
        model = Task
        fields = "__all__"
        exclude = ['project', ]
        
class TaskUpdateForm(CustomBaseForm):
    class Meta:
        model = TaskUpdate
        fields = "__all__"     
        exclude = ['task', 'submitted_by']