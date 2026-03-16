from django.urls import path
from .views import *

urlpatterns = [
    path("", ProjectListView.as_view(), name="project-index"),
    path("create", ProjectCreateView.as_view(), name="project-create"),
    path("<int:pk>/detail", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:pk>/update", ProjectUpdateView.as_view(), name="project-update"),
    path("<int:pk>/toggle/active", ProjectToggleActiveView.as_view(), name="project-toggle-active"),
    path("<int:pk>/delete", ProjectDeleteView.as_view(), name="project-delete"),
    
    path("projects/<int:pk>/disciplines/", ProjectDisciplineUpdateView.as_view(), name="project-disciplines"),
]