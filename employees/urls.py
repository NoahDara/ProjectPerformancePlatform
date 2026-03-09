# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("", EmployeeListView.as_view(), name="employee-index"),
    path("create", EmployeeCreateView.as_view(), name="employee-create"),
    path("<int:pk>/detail", EmployeeDetailView.as_view(), name="employee-detail"),
    path("<int:pk>/update", EmployeeUpdateView.as_view(), name="employee-update"),
    path("<int:pk>/toggle/active", EmployeeToggleActiveView.as_view(), name="employee-toggle-active"),
    path("<int:pk>/delete", EmployeeDeleteView.as_view(), name="employee-delete"),
]