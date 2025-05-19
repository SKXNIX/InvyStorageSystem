import io
from django import forms
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, response
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView

from apps.administrator import forms as admin_forms
from apps.custom_auth.models import CustomUser
from apps.core.mixins import RoleRequiredMixin
from apps.core.decorators import role_required

import pandas as pd
import random
import string


class UserListView(ListView):
    """Представление: список пользователей"""
    model = CustomUser
    template_name = 'admin_panel/users.html'
    context_object_name = 'users'
    # paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.GET.get('sort_by', 'id')
        order = self.request.GET.get('order', 'asc')

        if order == 'desc':
            sort_by = '-' + sort_by
        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by'] = self.request.GET.get('sort_by', 'id')
        context['order'] = self.request.GET.get('order', 'asc')
        return context


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
        context['action'] = 'создания'
        return context

    def form_valid(self, form):
        form.instance.password = make_password(form.cleaned_data['password'])
        return super().form_valid(form)

class UserUpdateView(UpdateView):
    """Представление: изменение данных пользователя"""
    model = CustomUser
    template_name = 'admin_panel/user_form.html'
    success_url = reverse_lazy('admin:users')

    form_class = admin_forms.UserUpdateForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_to_delete'] = self.get_object()
        return context

    def delete(self, request, *args, **kwargs):
        user_to_delete = self.get_object()
        if user_to_delete == request.user:
            messages.error(request, "Действие запрещено")
            return HttpResponseRedirect(reverse_lazy('users'))
        return super().delete(request, *args, **kwargs)

class DeleteSelectedUsersView(RoleRequiredMixin, FormView):
    allowed_roles = ['superadmin']

    def post(self, request):
        selected_users = request.POST.getlist('selected_users')
        if not selected_users:
            messages.warning(request, "Нет выбранных пользователей")
            return JsonResponse({'success': False, 'message': 'Нет выбранных пользователей'}, status=400)

        try:
            user_ids = list(map(int, selected_users))
            CustomUser.objects.filter(id__in=user_ids).delete()
            messages.success(request, "Выбранные пользователи удалены")
            return JsonResponse({'success': True})
        except (ValueError, CustomUser.DoesNotExist) as e:
            messages.warning(request, f"Ошибка при удалении пользователей {e}")
            return JsonResponse({"success": False, "message": f"Ошибка при удалении {e}"}, status=400)

class PasswordResetView(RoleRequiredMixin, FormView):
    """Представление: сброс пароля пользователя"""
    allowed_roles = ['superadmin']
    template_name = 'admin_panel/password_reset.html'
    success_url = reverse_lazy('admin:users')
    form_class = admin_forms.PasswordForm

    def get_success_url(self):
        return reverse_lazy('admin:user-update', args=[self.kwargs.get('pk')])

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

class ImportUsersView(RoleRequiredMixin, FormView):
    allowed_roles = ['superadmin']
    form_class = admin_forms.UploadExcelForm
    template_name = 'admin_panel/import_users.html'
    success_url = reverse_lazy('admin:users')

    def form_valid(self, form):
        file = form.cleaned_data['file']
        df = pd.read_excel(file)
        output = io.BytesIO()

        df['Username'] = ''
        df['Password'] = ''
        df['Status'] = ''

        success_count = 0
        error_rows = []

        required_columns = ['Full name', 'Role']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messages.error(self.request, f"Файл должен содержать столбцы: {', '.join(required_columns)}")
            return super().form_invalid(form)

        for idx, row in df.iterrows():
            try:
                # Проверка обязательных полей
                full_name = self._clean_field(row.get('Full name', ''))
                if not full_name:
                    raise ValueError("Поле 'Full name' должно быть заполнено")

                role = self._clean_field(row.get('Role', '')).lower()
                if not role:
                    raise ValueError("Поле 'Full name' должно быть заполнено")

                # Обработка username
                username = self._generate_username(full_name)
                if CustomUser.objects.filter(username=username).exists():
                    raise ValueError(f'Логин "{username}" уже существует')

                # Обработка password
                password = self._generate_password()

                if role == 'superadmin':
                    role = 'admin'
                    raise ValueError("Роль 'superadmin' недоступна для импорта")

                # Создание пользователя
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    full_name=full_name,
                    role=role)
                success_count += 1

                # Заполнение данных
                df.at[idx, 'Username'] = username
                df.at[idx, 'Password'] = password
                df.at[idx, 'Status'] = "Успешно"

            except Exception as e:
                df.at[idx, 'Status'] = str(e)
                error_rows.append(f'Ошибка в строке {idx + 2}: {str(e)}')
        
        if error_rows:
            messages.error(self.request, "Ошибки в следующих строках:\n" + "\n".join(error_rows))

        # Перенос DataFrame в Excel формат
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # Отправка файла с результатами
        response = HttpResponse(output.read(), 
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=import_result_{pd.Timestamp.now():%Y%m%d-%H%M%S}.xlsx'

        # Уведомление
        messages.success(self.request, f'Успешно добавлено: {success_count} пользователей')

        return response

    def _clean_field(self, value):
        if pd.isna(value):
            return ''
        return str(value).strip()

    def _generate_username(self, full_name):
        """Генерация случайного логина"""
        parts = full_name.split()
        if not parts:
            raise ValueError("Имя не указано для генерации username")

        base = parts[0].lower()
        for _ in range(100):
            suffix = ''.join(random.choices(string.digits, k=4))
            username = f'{base}{suffix}'
            if not CustomUser.objects.filter(username=username).exists():
                return username
        raise ValueError("Не удалось сгенерировать уникальный username")

    def _generate_password(self):
        """Генерация случайного пароля"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))


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