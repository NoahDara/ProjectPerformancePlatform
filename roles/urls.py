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
    path('roles/update/<int:pk>/', RoleUpdateView.as_view(), name='role-update'),
    path('roles/detail/<int:pk>/', RoleDetailView.as_view(), name='role-details'),
    path('roles/delete/<int:pk>/', RoleDeleteView.as_view(), name='role-delete'),
    path('roles/toggle-active/<int:pk>/', RoleToggleActiveView.as_view(), name='role-toggle-active'),
]
