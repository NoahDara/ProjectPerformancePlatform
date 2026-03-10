from django import forms
from django.contrib.auth import get_user_model
from helpers.forms import CustomBaseForm
User = get_user_model()
class CustomUserCreationForm(CustomBaseForm):
    class Meta:
        model = User
        fields = ["role",]

class ProfileUpdateForm(CustomBaseForm):
    class Meta:
        model = User
        fields = ("username", "first_name",  "last_name", "email",)
        
class CustomUserUpdateForm(CustomBaseForm):
    class Meta:
        model = User
        fields = ["role",]
class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)