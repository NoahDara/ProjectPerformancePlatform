from django.urls import path
from .views import (
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskToggleActiveView,
    TaskToggleStatusView
)

urlpatterns = [
    path("create/project/<int:pk>", TaskCreateView.as_view(), name="task-create"),
    path("<int:pk>/update", TaskUpdateView.as_view(), name="task-update"),
    path("<int:pk>/toggle/active", TaskToggleActiveView.as_view(), name="task-toggle-active"),
    path("<int:pk>/delete", TaskDeleteView.as_view(), name="task-delete"),
    path("<int:pk>/toggle/status", TaskToggleStatusView.as_view(), name="task-toggle-status"),
]
