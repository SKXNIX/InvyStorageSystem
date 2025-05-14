from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView

from apps.custom_auth.models import CustomUser
from apps.core.mixins import RoleRequiredMixin
from apps.core.decorators import role_required


class UserListView(ListView):
    """Представление: список пользователей"""
    model = CustomUser
    template_name = 'admin_panel/users.html'
    context_object_name = 'users'

class UserCreateView(CreateView):
    """Представление: создание нового пользователя"""
    model = CustomUser
    template_name = 'admin_panel/user_form.html'
    fields = ['username', 'password', 'full_name', 'role', 'avatar']
    success_url = reverse_lazy('admin:users')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['role'].choices = [
            (key, val) for key, val in CustomUser.ROLE_CHOICES
            if key != 'superadmin']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создание'
        return context

    def form_valid(self, form):
        form.instance.password = make_password(form.cleaned_data['password'])
        return super().form_valid(form)

class UserUpdateView(UpdateView):
    """Представление: изменение данных пользователя"""
    model = CustomUser
    template_name = 'admin_panel/user_form.html'
    success_url = reverse_lazy('admin:users')

    class UserForm(forms.ModelForm):
        class Meta:
            model = CustomUser
            fields = ['username', 'full_name', 'role', 'avatar']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance.role == 'superadmin':
                self.fields['role'].disabled = True
                self.fields['role'].help_text = "Роль суперадмина нельзя изменить"

    form_class = UserForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['role'].choices = [
            (key, val) for key, val in CustomUser.ROLE_CHOICES
            if key != 'superadmin']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Изменение'
        return context

class UserDeleteView(RoleRequiredMixin, DeleteView):
    """Представление: удаление пользователя"""
    model = CustomUser
    allowed_roles = ['superadmin']
    template_name = 'admin_panel/user_confirm_delete.html'
    success_url = reverse_lazy('admin:users')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            messages.error(request, "Действие запрещено")
            return HttpResponseRedirect(reverse_lazy('users'))
        return super().delete(request, *args, **kwargs)

class PasswordResetView(RoleRequiredMixin, FormView):
    """Представление: сброс пароля пользователя"""
    allowed_roles = ['superadmin']
    template_name = 'admin_panel/password_reset.html'
    success_url = reverse_lazy('admin:users')

    class PasswordForm(forms.Form):
        new_password = forms.CharField(
            label="Новый пароль",
            widget=forms.PasswordInput,
            required=True)

    form_class = PasswordForm

    def form_valid(self, form):
        user_id = self.kwargs.get('pk')
        new_password = form.cleaned_data['new_password']
        try:
            user = CustomUser.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            messages.success(self.request, "Пароль успешно изменён")
        except CustomUser.DoesNotExist:
            messages.error(self.request, "Пользователь не найден")
        return super().form_valid(form)


@login_required
@role_required(['superadmin'])
def admin_panel(request):
    """Админ-панель"""
    return render(request, 'admin_panel/index.html')

@login_required
@role_required(['superadmin'])
def user_list(request):
    """Список пользователей"""
    users = CustomUser.objects.all()
    return render(request, 'admin_panel/users.html', {'users': users})

@login_required
@role_required(['superadmin'])
def content(request):
    """Дополнительная страница"""
    content = "CONTENT"
    return render(request, 'admin_panel/content.html', {'content': content})

@login_required
@role_required(['superadmin'])
def settings(request):
    """Дополнительная страница"""
    settings = [1, 2, 3]
    return render(request, 'admin_panel/settings.html', {'settings': settings})


def create_superuser(request):
    """Функция-представление: создание superuser"""
    if CustomUser.objects.filter(is_superuser=True).exists():
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = CustomUser.objects.create_superuser(username, email, password)
        user.role = 'superadmin'
        user.save()

        return redirect('/')

    return render(request, 'custom_auth/create_superuser.html')