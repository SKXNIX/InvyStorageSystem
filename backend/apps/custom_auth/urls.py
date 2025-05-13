from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView


app_name = 'auth'

urlpatterns = [
    #path('login/', views.CustomLoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='auth:login'
    ), name='logout'),
]
