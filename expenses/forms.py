from helpers.forms import CustomBaseForm
from .models import ExpenseCategory, Expense

class ExpenseCategoryForm(CustomBaseForm):
    class Meta:
        model = ExpenseCategory
        fields = "__all__"
        
        
class ExpenseForm(CustomBaseForm):
    class Meta:
        model = Expense
        fields = "__all__"
        exclude = ["project",]