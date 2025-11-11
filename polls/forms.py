from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']