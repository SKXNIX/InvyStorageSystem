from django.urls import path
from django.contrib.auth import views as auth_views
import apps.custom_auth.views as views


app_name = 'auth'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='auth:login'), name='logout'),
    
]
