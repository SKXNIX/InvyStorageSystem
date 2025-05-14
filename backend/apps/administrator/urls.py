from django.urls import path
from django.contrib.auth.decorators import login_required
import apps.administrator.views as views

app_name = 'administrator'

urlpatterns = [
    path('', views.admin_panel, name='admin-panel'),    # Админ-панель
    path('content/', views.content, name='content'),    # Доп страница
    path('settings/', views.settings, name='settings'), # Доп страница

    path('users/', views.UserListView.as_view(), name='users'),                                                 # Список пользователей
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),                                  # Создание пользователя
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),                         # Изменение пользователя
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),                         # Удаление пользователя
    path('users/<int:pk>/reset-password/', views.PasswordResetView.as_view(), name='user-reset-password'),      # Сброс пароля
]