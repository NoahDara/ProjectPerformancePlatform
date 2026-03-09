from helpers.views import SafeListView, SafeUpdateView , SafeDeleteView, ToggleActiveView
from .models import Branch
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BranchForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
import random

class BranchListView(LoginRequiredMixin, SafeListView):
    model = Branch
    template_name = "branches/index.html"
    context_object_name = "branches"
    
class BranchCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Branch
    template_name = "branches/create.html"
    form_class = BranchForm
    success_url = reverse_lazy("branch-index")
    success_message = "Branch Created Successfully"
    
class BranchUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Branch
    context_object_name = "branch"
    template_name = "branches/update.html"
    form_class = BranchForm
    success_url = reverse_lazy("branch-index")
    
class BranchDetailView(LoginRequiredMixin, DetailView):
    model = Branch
    template_name = "branches/detail.html"
    context_object_name = "branch"
    
class BranchDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Branch
    success_url = reverse_lazy("branch-index")
    
class BranchToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Branch
    success_url = reverse_lazy("branch-index")