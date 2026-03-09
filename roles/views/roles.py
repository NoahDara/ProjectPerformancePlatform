from helpers.views import SafeListView, SafeUpdateView , SafeDeleteView, ToggleActiveView
from ..models import Role
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import RoleForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from roles.models import Role, CustomPermission
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict
from django.contrib.messages.views import SuccessMessageMixin

class RoleListView(LoginRequiredMixin, SafeListView):
    model = Role
    template_name = "roles/index.html"
    context_object_name = "roles"
    

class RoleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Role
    template_name = "roles/create.html"
    form_class = RoleForm
    success_message = "Role Created Successfully"
    success_url = reverse_lazy("role-index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grouped_permissions = defaultdict(list)
        for perm in CustomPermission.objects.filter(is_active=True).select_related('content_type'):
            grouped_permissions[perm.content_type].append(perm)

        context["grouped_permissions"] = grouped_permissions.items()
        return context

class RoleUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Role
    context_object_name = "role"
    template_name = "roles/update.html"
    form_class = RoleForm
    success_url = reverse_lazy("role-index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grouped_permissions = defaultdict(list)

        # Permissions already assigned to this role
        assigned_permissions = set(self.object.permissions.values_list('pk', flat=True))

        # Grouping all available permissions for display
        for perm in CustomPermission.objects.filter(is_active=True).select_related('content_type'):
            grouped_permissions[perm.content_type].append({
                "pk": perm.pk,
                "display_name": perm.display_name,
                "checked": perm.pk in assigned_permissions
            })

        context["grouped_permissions"] = grouped_permissions.items()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Update permissions from request
        permission_pks = self.request.POST.getlist("permissions")
        self.object.permissions.set(permission_pks)
        return response
    
class RoleDetailView(LoginRequiredMixin, DetailView):
    model = Role
    template_name = "roles/detail.html"
    context_object_name = "role"
    
class RoleDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Role
    success_url = reverse_lazy("role-index")
    
class RoleToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = Role
    success_url = reverse_lazy("role-index")