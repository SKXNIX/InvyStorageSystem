from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import LoginForm

from apps.custom_auth.models import CustomUser


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'custom_auth/login.html'  # Указываем точный путь к шаблону

    # Опционально: можно явно указать, что используем шаблон из текущего приложения
    def get_template_names(self):
        return ['custom_auth/login.html']

    def get_success_url(self):
        if self.request.user.is_superuser:
            return '/admin-panel/'
        else:
            return super().get_success_url()


