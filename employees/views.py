# views.py
from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView, ToggleActiveView
from .models import Employee
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import EmployeeForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin


class EmployeeListView(LoginRequiredMixin, SafeListView):
    model = Employee
    template_name = "employees/index.html"
    context_object_name = "employees"


class EmployeeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Employee
    template_name = "employees/create.html"
    form_class = EmployeeForm
    success_url = reverse_lazy("employee-index")
    success_message = "Employee Created Successfully"


class EmployeeUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Employee
    context_object_name = "employee"
    template_name = "employees/update.html"
    form_class = EmployeeForm
    success_url = reverse_lazy("employee-index")


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = "employees/detail.html"
    context_object_name = "employee"


class EmployeeDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Employee
    success_url = reverse_lazy("employee-index")


class EmployeeToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Employee
    success_url = reverse_lazy("employee-index")