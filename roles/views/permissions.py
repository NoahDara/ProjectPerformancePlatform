from helpers.views import SafeListView
from django.contrib.auth.mixins import LoginRequiredMixin
from roles.mixins import RequiredPermissionMixin
from ..models import CustomPermission

class CustomPermissionListView(LoginRequiredMixin, RequiredPermissionMixin, SafeListView):
    model = CustomPermission
    template_name = 'roles/permissions/index.html'
    context_object_name = 'permissions'
    
    # def required_permissions(self):
    #     return ["read_permission",]