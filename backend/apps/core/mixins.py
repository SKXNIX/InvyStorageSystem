from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Миксины для представлений
    в целях ограничения доступа по ролям
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)