from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView, TemplateView, UpdateView, CreateView
from django.views import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponse as HttpResponse
from django.contrib.auth import get_user_model

from helpers.emails import send_onboarding_reset_password_mail
User = get_user_model()
from ..forms import CustomUserCreationForm, CustomUserUpdateForm, LoginForm, ProfileUpdateForm
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from employees.models import Employee


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/index.html"
    context_object_name = "users"


class UserCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Creates a user account from an existing Employee.
    Inherits first_name, last_name, email, and username from the employee.
    Only requires the user to select a role.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = "accounts/create.html"
    success_message = "User account created successfully"

    def get_employee(self):
        return get_object_or_404(Employee, pk=self.kwargs["employee_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employee"] = self.get_employee()
        return context

    def form_valid(self, form):
        employee = self.get_employee()

        user = form.save(commit=False)
        user.first_name = employee.first_name
        user.last_name = employee.last_name
        user.email = employee.email
        user.username = employee.email  
        user.save()

        # Link the user back to the employee
        employee.user = user
        employee.save()
        
        try:
            send_onboarding_reset_password_mail(self.request, user)
        except Exception:
            user.set_password("IQ#2026")
            user.save()
            messages.error(
                self.request,
                "An error occurred sending the welcome email. "
                "A temporary password has been set: IQ#2026"
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("employee-index")


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Allows admins to update a user's role.
    """
    model = User
    form_class = CustomUserUpdateForm
    template_name = "accounts/update.html"
    success_message = "User updated successfully"
    context_object_name = "user_obj"  

    def get_success_url(self):
        return reverse("users-index")


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Allows a user to update their own profile details.
    """
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"
    success_message = "Profile updated successfully"

    def get_object(self, queryset=None):
        # Always update the currently logged-in user
        return self.request.user

    def get_success_url(self):
        return reverse("profile-update")

        

class UserDeleteView(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        obj = User.objects.get(pk=self.request.GET.get('pk'))
        obj.is_deleted = True
        obj.save()
        messages.warning(self.request, 'User Deleted successfully')
        return redirect('users-index')   

     
class UserDeactivateView(LoginRequiredMixin, SuccessMessageMixin, View):
    def get(self, request, **kwargs):
        obj = get_object_or_404(User, pk=kwargs.get("pk"))
        if obj.is_active:
            obj.is_active = False
            messages.success(request, f"{obj} has been deactivated successfully")
        else:
            obj.is_active = True
            messages.success(request, f"{obj} has been activated successfully")
        obj.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
