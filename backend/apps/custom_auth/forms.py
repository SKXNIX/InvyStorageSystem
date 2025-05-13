from django.contrib.auth.forms import AuthenticationForm
from django import forms

class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': 'Логин'
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Пароль'
        })