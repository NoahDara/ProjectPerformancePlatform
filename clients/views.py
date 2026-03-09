from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView, ToggleActiveView
from .models import Client
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ClientForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin


class ClientListView(LoginRequiredMixin, SafeListView):
    model = Client
    template_name = "clients/index.html"
    context_object_name = "clients"


class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    template_name = "clients/create.html"
    form_class = ClientForm
    success_url = reverse_lazy("client-index")
    success_message = "Client Created Successfully"


class ClientUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Client
    context_object_name = "client"
    template_name = "clients/update.html"
    form_class = ClientForm
    success_url = reverse_lazy("client-index")


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "clients/detail.html"
    context_object_name = "client"


class ClientDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Client
    success_url = reverse_lazy("client-index")


class ClientToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Client
    success_url = reverse_lazy("client-index")