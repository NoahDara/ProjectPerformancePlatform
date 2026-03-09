from helpers.forms import CustomBaseForm
from .models import Discipline, Position

class DisciplineForm(CustomBaseForm):
    class Meta:
        model = Discipline
        fields = "__all__"
        
class PositionForm(CustomBaseForm):
    class Meta:
        model = Position
        fields = "__all__"