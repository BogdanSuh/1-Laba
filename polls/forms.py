# polls/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=True, label='Аватар')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Profile уже создан сигналом, но аватар нужно обновить
            if self.cleaned_data.get('avatar'):
                user.profile.avatar = self.cleaned_data['avatar']
                user.profile.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(required=True, label='Аватар')

    class Meta:
        model = Profile
        fields = ["avatar", "bio", "location"]