from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView, DeleteView, TemplateView, FormView, UpdateView
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponse as HttpResponse
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.hashers import make_password
from ..forms import CustomUserCreationForm, CustomUserUpdateForm, LoginForm
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin


def logout_view(request):
    logout(request)
    return redirect('login')

class LoginUserView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("dashboard")  

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)

            employee = getattr(user, "employee", None)
            
            if user.is_active:
                if employee:
                    messages.success(self.request, f"You have successfully logged in as {employee}")
                else:
                    messages.success(self.request, f"You have successfully logged in as {user}")
            else:
                messages.warning(self.request, "Your account is inactive. Please contact system administrator.")

            # Handle the 'next' parameter for redirection
            next_url = self.request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
                return redirect(next_url)
            
            # Default to success_url if 'next' is not set or not safe
            return super().form_valid(form)
        else:
            messages.warning(
                self.request, "Please check your credentials and try again"
            )
            return redirect("login")

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)