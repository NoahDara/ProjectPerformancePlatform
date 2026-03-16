from django.urls import path
from .views import (
    ExpenseCategoryListView, ExpenseCategoryCreateView,
    ExpenseCategoryUpdateView, ExpenseCategoryDetailView,
    ExpenseCategoryDeleteView, ExpenseCategoryToggleActiveView,
    GenerateExpenseCategoriesView,
    
    ExpenseListView, ExpenseCreateView, ExpenseUpdateView,
    ExpenseDetailView, ExpenseDeleteView, ExpenseToggleStatusView
)

urlpatterns = [    
    path("categories", ExpenseCategoryListView.as_view(), name="expense-category-index"),
    path("category/create", ExpenseCategoryCreateView.as_view(), name="expense-category-create"),
    path("category/<int:pk>/detail", ExpenseCategoryDetailView.as_view(), name="expense-category-details"),
    path("category/<int:pk>/update", ExpenseCategoryUpdateView.as_view(), name="expense-category-update"),
    path("category/<int:pk>/toggle/active", ExpenseCategoryToggleActiveView.as_view(), name="expense-category-toggle-active"),
    path("category/<int:pk>/delete", ExpenseCategoryDeleteView.as_view(), name="expense-category-delete"),
    path('generate-expense-categories/', GenerateExpenseCategoriesView.as_view(), name='generate-expense-categories'),
    
    path("", ExpenseListView.as_view(), name="expense-index"),
    path("create", ExpenseCreateView.as_view(), name="expense-create"),
    path("<int:pk>/update", ExpenseUpdateView.as_view(), name="expense-update"),
    path("<int:pk>/detail", ExpenseDetailView.as_view(), name="expense-details"),
    path("<int:pk>/delete", ExpenseDeleteView.as_view(), name="expense-delete"),
    path("<int:pk>/toggle/status", ExpenseToggleStatusView.as_view(), name="expense-toggle-status"),
]