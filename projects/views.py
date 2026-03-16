from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView, ToggleActiveView
from .models import Project, ProjectDiscipline
from .forms import ProjectForm, ProjectDisciplineForm
from django.views.generic import CreateView, DetailView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect

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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        from django.utils import timezone
        from django.db.models import Sum

        # Overall weighted progress
        disciplines = project.disciplines.prefetch_related('tasks__updates').all()
        ctx['overall_progress'] = round(sum(
            pd.percent_complete * float(pd.planned_weight) / 100
            for pd in disciplines
        ), 1)
        ctx['total_actual_cost'] = 100
        ctx['budget_remaining'] = float(project.baseline_budget or 0) - ctx['total_actual_cost']
        ctx['budget_variance_pct'] = (
            ctx['total_actual_cost'] / float(project.baseline_budget) * 100
            if project.baseline_budget else None
        )
        if project.baseline_end_date:
            ctx['schedule_variance'] = (project.planned_end_date - project.baseline_end_date).days
        else:
            ctx['schedule_variance'] = 0
        ctx['days_remaining'] = (project.planned_end_date - timezone.now().date()).days
        expenses = project.expenses.all()
        ctx['expense_total'] = expenses.aggregate(t=Sum('amount'))['t'] or 0
        ctx['expense_confirmed'] = expenses.filter(status='Confirmed').aggregate(t=Sum('amount'))['t'] or 0
        ctx['expense_pending'] = expenses.filter(status='Submitted').aggregate(t=Sum('amount'))['t'] or 0

        return ctx

class ProjectDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Project
    success_url = reverse_lazy("project-index")


class ProjectToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Project
    success_url = reverse_lazy("project-index")


class ProjectDisciplineUpdateView(LoginRequiredMixin, View):
    template_name = "projects/disciplines/update.html"

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
            return redirect(reverse("project-details", kwargs={"pk": pk}))

        return render(request, self.template_name, {
            "project": project,
            "formset": formset,
        })
        
class ProjectToggleStatusView(View):
    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        status = request.POST.get("status")
        if status in dict(Project.STATUS_CHOICES):        
            project.status = status
            project.save(update_fields=["status"])
        messages.info(request, f"Project status updated successfully to {project.get_status_display()}")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER") or "/")