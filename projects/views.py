from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView, ToggleActiveView
from .models import Project, ProjectDiscipline
from .forms import ProjectForm, ProjectDisciplineForm
from django.views.generic import CreateView, DetailView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect


class ProjectListView(LoginRequiredMixin, SafeListView):
    model = Project
    template_name = "projects/index.html"
    context_object_name = "projects"


class ProjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Project
    template_name = "projects/create.html"
    form_class = ProjectForm
    success_message = "Project Created Successfully"

    def get_success_url(self):
        return reverse("project-disciplines", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Project
    context_object_name = "project"
    template_name = "projects/update.html"
    form_class = ProjectForm
    success_url = reverse_lazy("project-index")


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"


class ProjectDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Project
    success_url = reverse_lazy("project-index")


class ProjectToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Project
    success_url = reverse_lazy("project-index")


class ProjectDisciplineUpdateView(LoginRequiredMixin, View):
    template_name = "projects/disciplines.html"

    def get_project(self, pk):
        return get_object_or_404(Project, pk=pk)

    def get_formset_class(self):
        return modelformset_factory(
            ProjectDiscipline,
            form=ProjectDisciplineForm,
            extra=0,
        )

    def get(self, request, pk):
        project = self.get_project(pk)
        ProjectDisciplineFormSet = self.get_formset_class()
        formset = ProjectDisciplineFormSet(
            queryset=ProjectDiscipline.objects.filter(project=project).select_related('discipline', 'manager')
        )
        return render(request, self.template_name, {
            "project": project,
            "formset": formset,
        })

    def post(self, request, pk):
        project = self.get_project(pk)
        ProjectDisciplineFormSet = self.get_formset_class()
        formset = ProjectDisciplineFormSet(
            request.POST,
            queryset=ProjectDiscipline.objects.filter(project=project).select_related('discipline', 'manager')
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Disciplines updated successfully.")
            return redirect(reverse("project-detail", kwargs={"pk": pk}))

        return render(request, self.template_name, {
            "project": project,
            "formset": formset,
        })