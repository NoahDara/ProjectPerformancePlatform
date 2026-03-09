from helpers.forms import CustomBaseForm
from .models import Employee

class EmployeeForm(CustomBaseForm):
    class Meta:
        model = Employee
        fields = "__all__"
        exclude = ['user', ]