from django.contrib.auth.views import LoginView
from django.shortcuts import render
from .forms import LoginForm


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'custom_auth/login.html'  # Указываем точный путь к шаблону

    # Опционально: можно явно указать, что используем шаблон из текущего приложения
    def get_template_names(self):
        return ['custom_auth/login.html']
