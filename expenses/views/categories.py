from helpers.views import SafeListView, SafeUpdateView , SafeDeleteView, ToggleActiveView
from ..models import ExpenseCategory
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import ExpenseCategoryForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings

class ExpenseCategoryListView(LoginRequiredMixin, SafeListView):
    model = ExpenseCategory
    template_name = "expenses/categories/index.html"
    context_object_name = "categories"
    
class ExpenseCategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExpenseCategory
    template_name = "expenses/categories/create.html"
    form_class = ExpenseCategoryForm
    success_url = reverse_lazy("expense-category-index")
    success_message = "Expense Category Created Successfully"
    
class ExpenseCategoryUpdateView(LoginRequiredMixin, SafeUpdateView):
    model = ExpenseCategory
    context_object_name = "category"
    template_name = "expenses/categories/update.html"
    form_class = ExpenseCategoryForm
    success_url = reverse_lazy("expense-category-index")
    
class ExpenseCategoryDetailView(LoginRequiredMixin, DetailView):
    model = ExpenseCategory
    template_name = "expenses/categories/detail.html"
    context_object_name = "category"
    
class ExpenseCategoryDeleteView(LoginRequiredMixin, SafeDeleteView):
    model = ExpenseCategory
    success_url = reverse_lazy("expense-category-index")
    
class ExpenseCategoryToggleActiveView(LoginRequiredMixin, ToggleActiveView):
    model = ExpenseCategory
    success_url = reverse_lazy("expense-category-index")
    
    
from django.http import HttpResponseRedirect
from django.contrib import messages


class GenerateExpenseCategoriesView(LoginRequiredMixin, TemplateView):
    
    def get(self, request, *args, **kwargs):
        categories = [
            {"name": "Fuel", "description": "Fuel for drilling rigs, transport vehicles, and generators."},
            {"name": "Food", "description": "Meals and refreshments for workers on-site."},
            {"name": "Equipment Maintenance", "description": "Repairs, servicing, and maintenance of drilling equipment."},
            {"name": "Labour", "description": "Wages, allowances, and overtime for drilling crew and support staff."},
            {"name": "Permits & Fees", "description": "Government drilling permits, licenses, and environmental fees."},
            {"name": "Transportation", "description": "Vehicle hire, transport costs, and logistics expenses."},
            {"name": "Accommodation", "description": "Lodging costs for crew working on remote sites."},
            {"name": "Tools & Consumables", "description": "Small tools, drill bits, pipes, and consumable materials."},
            {"name": "Water & Utilities", "description": "Water supply for drilling operations and utility bills."},
            {"name": "Safety Equipment", "description": "PPE, safety gear, and health and safety compliance costs."},
            {"name": "Communication", "description": "Airtime, internet, and communication services."},
            {"name": "Site Preparation", "description": "Land clearing, access road construction, and site setup."},
            {"name": "Subcontractor Payments", "description": "Payments to external contractors and specialists."},
            {"name": "Office Expenses", "description": "Stationery, printing, and administrative supplies."},
            {"name": "Insurance", "description": "Equipment insurance, liability insurance, and worker compensation."},
            {"name": "Legal & Professional Fees", "description": "Legal services, consulting, and professional advisory fees."},
            {"name": "Marketing & Advertising", "description": "Promotional materials, advertisements, and marketing campaigns."},
            {"name": "Training & Development", "description": "Staff training, workshops, and skills development programs."},
            {"name": "Bank Charges", "description": "Bank fees, transaction charges, and loan interest."},
            {"name": "Miscellaneous", "description": "Other miscellaneous operational expenses."},
        ]
        
        try:
            categories_created = 0
            categories_skipped = 0
            
            for category in categories:
                if not ExpenseCategory.objects.filter(name=category["name"]).exists():
                    ExpenseCategory.objects.create(
                        name=category["name"],
                        code=category["name"],
                        description=category["description"]
                    )
                    categories_created += 1
                else:
                    categories_skipped += 1
            
            if categories_created > 0:
                messages.success(request, f'Successfully created {categories_created} expense categories.')
            if categories_skipped > 0:
                messages.info(request, f'{categories_skipped} expense categories already existed and were skipped.')
            
            if categories_created == 0 and categories_skipped == 0:
                messages.info(request, 'No expense categories to create.')
        
        except Exception as e:
            settings.LOGGER.error(f"Error creating expense categories: {str(e)} ")
            messages.error(request, f'Error creating expense categories: {str(e)}')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))