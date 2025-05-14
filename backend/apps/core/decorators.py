from django.http import HttpResponseForbidden


def role_required(allowed_roles=[]):
    """
    Декоратор для функций представлений
    в целях ограничения доступа по ролям
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("Not allowed")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator