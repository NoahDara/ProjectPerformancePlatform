from helpers.forms import CustomBaseForm
from .models import Branch

class BranchForm(CustomBaseForm):
    class Meta:
        model = Branch
        fields = "__all__"