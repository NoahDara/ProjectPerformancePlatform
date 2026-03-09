from django.urls import path
from .views import *

urlpatterns = [
    path("", ClientListView.as_view(), name="client-index"),
    path("create", ClientCreateView.as_view(), name="client-create"),
    path("<int:pk>/detail", ClientDetailView.as_view(), name="client-detail"),
    path("<int:pk>/update", ClientUpdateView.as_view(), name="client-update"),
    path("<int:pk>/toggle/active", ClientToggleActiveView.as_view(), name="client-toggle-active"),
    path("<int:pk>/delete", ClientDeleteView.as_view(), name="client-delete"),
]