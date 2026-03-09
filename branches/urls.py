from django.urls import path
from .views import *

urlpatterns = [
    path("", BranchListView.as_view(), name="branch-index"),
    path("create", BranchCreateView.as_view(), name="branch-create"),
    path("<int:pk>/detail", BranchDetailView.as_view(), name="branch-details"),
    path("<int:pk>/update", BranchUpdateView.as_view(), name="branch-update"),
    path("<int:pk>/toggle/active", BranchToggleActiveView.as_view(), name="branch-toggle-active"),
    path("<int:pk>/delete", BranchDeleteView.as_view(), name="branch-delete"),
]