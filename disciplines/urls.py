from django.urls import path
from .views import *

urlpatterns = [
    # ─── Discipline URLs ─────────────────────────────────────────────────────
    path("disciplines/", DisciplineListView.as_view(), name="discipline-index"),
    path("disciplines/create", DisciplineCreateView.as_view(), name="discipline-create"),
    path("disciplines/<int:pk>/detail", DisciplineDetailView.as_view(), name="discipline-detail"),
    path("disciplines/<int:pk>/update", DisciplineUpdateView.as_view(), name="discipline-update"),
    path("disciplines/<int:pk>/toggle/active", DisciplineToggleActiveView.as_view(), name="discipline-toggle-active"),
    path("disciplines/<int:pk>/delete", DisciplineDeleteView.as_view(), name="discipline-delete"),

    # ─── Position URLs ───────────────────────────────────────────────────────
    path("positions/", PositionListView.as_view(), name="position-index"),
    path("positions/create", PositionCreateView.as_view(), name="position-create"),
    path("positions/<int:pk>/detail", PositionDetailView.as_view(), name="position-detail"),
    path("positions/<int:pk>/update", PositionUpdateView.as_view(), name="position-update"),
    path("positions/<int:pk>/toggle/active", PositionToggleActiveView.as_view(), name="position-toggle-active"),
    path("positions/<int:pk>/delete", PositionDeleteView.as_view(), name="position-delete"),
]