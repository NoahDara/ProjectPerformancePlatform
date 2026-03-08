from django import forms
from .models import Role
from roles.models import CustomPermission
from django.contrib.contenttypes.models import ContentType

class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.filter(is_active=True).select_related('content_type'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Role
        exclude = ['is_active', 'is_deleted']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Add helper text to is_admin field
        self.fields['is_admin'].help_text = 'Users with this role will have access to the Admin Center'
        self.fields['is_admin'].widget.attrs['class'] = 'form-check-input'