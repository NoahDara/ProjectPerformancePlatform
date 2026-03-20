from django.http import HttpResponseRedirect
from helpers.views import SafeListView, SafeUpdateView, SafeDeleteView
from ..models import Expense
from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import ExpenseForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from projects.models import Project


ACTION_MAP = {
    'draft':     {'status': 'Draft',     'message': 'Expense Saved as Draft'},
    'submitted': {'status': 'Submitted', 'message': 'Expense Submitted for Approval'},
    'confirmed': {'status': 'Confirmed', 'message': 'Expense Confirmed Successfully'},
    'cancelled': {'status': 'Cancelled', 'message': 'Expense Cancelled'},
}


class ExpenseListView(LoginRequiredMixin, SafeListView):
    model = Expense
    template_name = "expenses/index.html"
    context_object_name = "expenses"


class ExpenseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Expense
    template_name = "expenses/create.html"
    form_class = ExpenseForm
    success_message = "Expense Created Successfully"

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_project()
        return context

    def form_valid(self, form):
        form.instance.project = self.get_project()
        form.instance.recorded_by = self.request.user

        submit_action = self.request.POST.get('submit_action', 'draft').lower()
        action = ACTION_MAP.get(submit_action, ACTION_MAP['draft'])
        form.instance.status = action['status']
        self.success_message = action['message']

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.get_project().pk})


class ExpenseUpdateView(LoginRequiredMixin, SuccessMessageMixin, SafeUpdateView):
    model = Expense
    context_object_name = "expense"
    template_name = "expenses/update.html"
    form_class = ExpenseForm
    success_message = "Expense Updated Successfully"

    def form_valid(self, form):
        old_status = self.get_object().status
        submit_action = self.request.POST.get('submit_action', '').lower()

        # Guard: confirmed expenses cannot go back to draft
        if old_status == 'Confirmed' and submit_action == 'draft':
            from django.contrib import messages
            messages.warning(self.request, "Cannot change a confirmed expense back to draft.")
            return self.form_invalid(form)

        action = ACTION_MAP.get(submit_action)
        if action:
            form.instance.status = action['status']
            self.success_message = action['message']
        else:
            form.instance.status = old_status 

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.object.project.pk})


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = "expenses/detail.html"
    context_object_name = "expense"


class ExpenseDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Expense

    def get_success_url(self):
        return reverse_lazy("project-details", kwargs={"pk": self.object.project.pk})


class ExpenseToggleStatusView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        expense = get_object_or_404(Expense, pk=kwargs["pk"])
        reason = request.POST.get("reason", "")
        status = request.POST.get("status")
        expense.status = status
        expense.save_with_reason(reason)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))