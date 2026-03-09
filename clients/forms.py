from helpers.forms import CustomBaseForm
from .models import Client

class ClientForm(CustomBaseForm):
    class Meta:
        model = Client
        fields = "__all__"