from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.views import SafeDeleteView, SafeUpdateView, ToggleActiveView
from projects.models import Project
from .models import Task, TaskUpdate
from .forms import TaskForm, TaskUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.
class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task 
    template_name = "tasks/create.html"
    form_class = TaskForm
    success_message = "New task has been added to the project"
    
    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def form_valid(self, form):
        project = self.get_object()
        form.instance.project = project
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object()
        return context
    
    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.get_object().pk})
    
class TaskUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Task
    context_object_name = "task"
    template_name = "tasks/update.html"
    form_class = TaskForm
    
    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.object.project.pk})
    
class TaskDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Task
    
    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.object.project.pk})
    
class TaskToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Task

    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.object.project.pk})
    
class TaskToggleStatusView(TemplateView):
    model = Task

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        reason = request.POST.get("reason", "")
        status = request.POST.get("status")
        task.status = status
        task.save_with_reason(reason)
        messages.info(request, f"Task status changed to {task.status}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
class TaskUpdateCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TaskUpdate  # Fix: should be TaskUpdate, not Task
    template_name = "tasks/updates/create.html"
    form_class = TaskUpdateForm
    success_message = "New task Progress Update has been added to the task"

    def get_object(self):
        return get_object_or_404(Task, pk=self.kwargs["pk"])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Assign task to instance BEFORE is_valid() calls clean()
        form.instance.task = self.get_object()
        return form

    def form_valid(self, form):
        form.instance.submitted_by = self.request.user.employee  # adjust to your user->employee relationship
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.get_object()
        return context

    def get_success_url(self):
        return reverse_lazy("task-progress-create", kwargs={"pk": self.kwargs["pk"]})
    
    
class TaskUpdateUpdateView(LoginRequiredMixin, SuccessMessageMixin, SafeUpdateView):
    model = TaskUpdate
    template_name = "tasks/updates/update.html"
    form_class = TaskUpdateForm
    success_message = "Task Progress Update has been updated successfully"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.get_object().task
        return context
    
    def get_success_url(self):
        return reverse_lazy("task-progress-create", kwargs={"pk": self.get_object().task.pk})