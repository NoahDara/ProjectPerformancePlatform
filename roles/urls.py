from django.urls import path
from .views import (
    CustomPermissionListView,
    
    RoleListView,
    RoleCreateView,
    RoleUpdateView,
    RoleDetailView,
    RoleDeleteView,
    RoleToggleActiveView
)

urlpatterns = [
    path('permissions/', CustomPermissionListView.as_view(), name='permission-index'),
    
    path('roles/', RoleListView.as_view(), name='role-index'),
    path('roles/create/', RoleCreateView.as_view(), name='role-create'),
    path('roles/update/<uuid:uid>/', RoleUpdateView.as_view(), name='role-update'),
    path('roles/detail/<uuid:uid>/', RoleDetailView.as_view(), name='role-details'),
    path('roles/delete/<uuid:uid>/', RoleDeleteView.as_view(), name='role-delete'),
    path('roles/toggle-active/<uuid:uid>/', RoleToggleActiveView.as_view(), name='role-toggle-active'),
]
