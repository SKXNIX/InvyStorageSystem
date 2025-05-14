from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
#from django.contrib.auth.models import User

from apps.custom_auth.models import CustomUser


class SuperuserRequiredMiddleware:
    """
    Middleware для создания superuser при первом запуске
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not CustomUser.objects.filter(is_superuser=True).exists():
            if not (request.path == reverse('create_superuser') 
                    or request.user.is_authenticated):
                return HttpResponseRedirect(reverse('create_superuser'))
        response = self.get_response(request)
        return response


class AdminPanelAccessMiddleware:
    """
    Middleware для автоперехода superuser на страницу админки
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin-panel/') and not request.user.is_superuser:
            return redirect('auth:login')
        response = self.get_response(request)
        return response