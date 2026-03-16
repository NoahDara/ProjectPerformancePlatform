from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.views import SafeDeleteView, SafeUpdateView, ToggleActiveView
from projects.models import Project
from .models import Task
from .forms import TaskForm
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.
class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Project 
    template_name = "tasks/create.html"
    form_class = TaskForm
    success_message = "New task has been added to the project"

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