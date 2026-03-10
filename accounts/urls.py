from django.urls import path
from . import views
from .views import (
    CustomPasswordResetView, 
    UserListView, 
    UserDeleteView, 
    LoginUserView,
    UserCreateView,
    UserUpdateView,
    ProfileUpdateView,
)

from django.contrib.auth import views as auth_views



urlpatterns = [

    path('users', UserListView.as_view(), name="users-index"),
    path("employee/<int:employee_pk>/create/", UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path('delete/', UserDeleteView.as_view(), name="delete-user"),
    path('deactivate/<int:pk>/', views.UserDeactivateView.as_view(), name="deactivate-user"),


    # user authentication
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', views. logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset_request'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='mail_list/emails/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='mail_list/emails/password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html', success_url='/home'), name="password_change"),
    path('reset/', CustomPasswordResetView.as_view(), name='password_reset'),
]
