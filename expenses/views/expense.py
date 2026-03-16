from django.http import HttpResponseRedirect
from helpers.views import SafeListView, SafeUpdateView , SafeDeleteView, ToggleActiveView
from ..models import Expense
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import ExpenseForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.contenttypes.models import ContentType


class ExpenseListView(LoginRequiredMixin, SafeListView):
    model = Expense
    template_name = "expenses/index.html"
    context_object_name = "expenses"
    
class ExpenseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Expense
    template_name = "expenses/create.html"
    form_class = ExpenseForm
    success_message = "Expense Created Successfully"
    
    def get_initial(self):
        """Pre-fill form with content_object if provided in URL"""
        initial = super().get_initial()
        
        # Get content_type and object_uid from query parameters
        content_type_id = self.request.GET.get('content_type')
        object_uid = self.request.GET.get('object')
        
        if content_type_id and object_uid:
            try:
                content_type = ContentType.objects.get(pk=content_type_id)
                initial['content_type'] = content_type
                initial['object_uid'] = object_uid
            except ContentType.DoesNotExist:
                pass
        
        return initial
    
    def get_form_kwargs(self):
        """Pass content_object to form"""
        kwargs = super().get_form_kwargs()
        
        # Get content_object if available
        content_type_id = self.request.GET.get('content_type')
        object_uid = self.request.GET.get('object')
        
        if content_type_id and object_uid:
            try:
                content_type = ContentType.objects.get(pk=content_type_id)
                model_class = content_type.model_class()
                content_object = model_class.objects.get(uid=object_uid)
                kwargs['content_object'] = content_object
            except (ContentType.DoesNotExist, model_class.DoesNotExist):
                kwargs['content_object'] = None
        else:
            kwargs['content_object'] = None
        
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add content_object to context for display"""
        context = super().get_context_data(**kwargs)
        
        content_type_id = self.request.GET.get('content_type')
        object_uid = self.request.GET.get('object')
        
        if content_type_id and object_uid:
            try:
                content_type = ContentType.objects.get(pk=content_type_id)
                model_class = content_type.model_class()
                content_object = model_class.objects.get(uid=object_uid)
                context['content_object'] = content_object
            except (ContentType.DoesNotExist, model_class.DoesNotExist):
                context['content_object'] = None
        
        return context

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        
        # Set content_type and object_uid from query params
        content_type_id = self.request.GET.get('content_type')
        object_uid = self.request.GET.get('object')
        
        if content_type_id and object_uid:
            try:
                content_type = ContentType.objects.get(pk=content_type_id)
                form.instance.content_type = content_type
                form.instance.object_uid = object_uid
            except ContentType.DoesNotExist:
                pass
        
        # Check which submit button was clicked
        submit_action = self.request.POST.get('submit_action', '').lower()
        
        # Map of actions to status values and success messages
        action_map = {
            'draft': {
                'status': 'Draft',
                'message': 'Expense Saved as Draft'
            },
            'submitted': {
                'status': 'Submitted',
                'message': 'Expense Submitted for Approval'
            },
            'confirmed': {
                'status': 'Confirmed',
                'message': 'Expense Confirmed Successfully'
            }
        }
        
        # If requires_approval is checked and user tries to confirm, submit instead
        if form.instance.requires_approval and submit_action == 'confirmed':
            submit_action = 'submitted'
        
        if submit_action in action_map:
            action_config = action_map[submit_action]
            form.instance.status = action_config['status']
            self.success_message = action_config['message']
        else:
            # Default to draft if no action specified
            form.instance.status = 'Draft'
            self.success_message = 'Expense Saved as Draft'
        
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Return the URL to redirect to after successful form submission.
        Uses content_object's expense_absolute_url if available.
        """
        if self.object.content_object and hasattr(self.object.content_object, 'expense_absolute_url'):
            return self.object.content_object.expense_absolute_url
        
        return reverse_lazy("expense-index")
    
class ExpenseUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = Expense
    context_object_name = "expense"
    template_name = "expenses/update.html"
    form_class = ExpenseForm
    success_message = "Expense Updated Successfully"
    
    def get_form_kwargs(self):
        """Pass content_object to form"""
        kwargs = super().get_form_kwargs()
        expense = self.get_object()
        kwargs['content_object'] = expense.content_object
        return kwargs
    
    def form_valid(self, form):
        # Check which submit button was clicked
        submit_action = self.request.POST.get('submit_action', '').lower()
        
        # Get the old status before updating
        old_status = self.get_object().status
        
        # Map of actions to status values and success messages
        action_map = {
            'draft': {
                'status': 'Draft',
                'message': 'Expense Saved as Draft'
            },
            'submitted': {
                'status': 'Submitted',
                'message': 'Expense Submitted for Approval'
            },
            'confirmed': {
                'status': 'Confirmed',
                'message': 'Expense Confirmed Successfully' if old_status != 'Confirmed' else 'Expense Updated'
            },
            'cancelled': {
                'status': 'Cancelled',
                'message': 'Expense Cancelled'
            }
        }
        
        # Prevent changing confirmed expenses back to draft
        if old_status == 'Confirmed' and submit_action == 'draft':
            from django.contrib import messages
            messages.warning(self.request, "Cannot change a confirmed expense back to draft")
            return self.form_invalid(form)
        
        # If requires_approval is checked and user tries to confirm, submit instead
        if form.instance.requires_approval and submit_action == 'confirmed':
            submit_action = 'submitted'
        
        if submit_action in action_map:
            action_config = action_map[submit_action]
            form.instance.status = action_config['status']
            self.success_message = action_config['message']
        else:
            # If no action specified, keep current status
            form.instance.status = old_status if old_status else 'Draft'
        
        return super().form_valid(form)

    def get_success_url(self):
        """Return custom success URL if content_object has expense_absolute_url"""
        if self.object.content_object and hasattr(self.object.content_object, 'expense_absolute_url'):
            return self.object.content_object.expense_absolute_url
        
        return reverse_lazy("expense-index")
    
    
class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = "expenses/detail.html"
    context_object_name = "expense"
    
class ExpenseDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = Expense
    
    def get_success_url(self):
        return reverse_lazy("job-details", kwargs={"uid": self.object.job.uid}) + "?tab=expenses"
    
    
class ExpenseToggleStatusView(TemplateView):
    model = Expense
    
    def get(self, request, *args, **kwargs):
        expense = self.get_object()
        status = self.request.GET.get("status")
        expense.status = status
        expense.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def post(self, request, *args, **kwargs):
        expense = self.get_object()
        reason = request.POST.get("reason", "")
        status = request.POST.get("status")
        expense.status = status
        expense.save_with_reason(reason)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))