from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView, ToggleActiveView
from .models import Discipline, Position
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import DisciplineForm, PositionForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin


# ─── Discipline Views ───────────────────────────────────────────────────────

class DisciplineListView(LoginRequiredMixin, SafeListView):
    model = Discipline
    template_name = "disciplines/index.html"
    context_object_name = "disciplines"


class DisciplineCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Discipline
    template_name = "disciplines/create.html"
    form_class = DisciplineForm
    success_url = reverse_lazy("discipline-index")
    success_message = "Discipline Created Successfully"


class DisciplineUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Discipline
    context_object_name = "discipline"
    template_name = "disciplines/update.html"
    form_class = DisciplineForm
    success_url = reverse_lazy("discipline-index")


class DisciplineDetailView(LoginRequiredMixin, DetailView):
    model = Discipline
    template_name = "disciplines/detail.html"
    context_object_name = "discipline"


class DisciplineDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Discipline
    success_url = reverse_lazy("discipline-index")


class DisciplineToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Discipline
    success_url = reverse_lazy("discipline-index")


# ─── Position Views ─────────────────────────────────────────────────────────

class PositionListView(LoginRequiredMixin, SafeListView):
    model = Position
    template_name = "positions/index.html"
    context_object_name = "positions"


class PositionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Position
    template_name = "positions/create.html"
    form_class = PositionForm
    success_url = reverse_lazy("position-index")
    success_message = "Position Created Successfully"


class PositionUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Position
    context_object_name = "position"
    template_name = "positions/update.html"
    form_class = PositionForm
    success_url = reverse_lazy("position-index")


class PositionDetailView(LoginRequiredMixin, DetailView):
    model = Position
    template_name = "positions/detail.html"
    context_object_name = "position"


class PositionDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Position
    success_url = reverse_lazy("position-index")


class PositionToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Position
    success_url = reverse_lazy("position-index")