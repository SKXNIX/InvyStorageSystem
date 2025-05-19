from django.urls import reverse
from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'core/index.html'
'''
class ProductManagementView(LoginRequiredMixin, TemplateView):
    template_name = "template_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Пример данных — позже можно заменить на реальные
        context['data'] = [
            ['Товар 1', 'Категория A', '10', 'ед.', '100₽', 'Склад 1', 'Поставщик 1', '01.01.2025', 'Комментарий', 'ID001'],
            ['Товар 2', 'Категория B', '5', 'ед.', '200₽', 'Склад 2', 'Поставщик 2', '05.01.2025', 'Комментарий', 'ID002'],
        ]
        return context
'''


@login_required
def StartPage(request):
    return render(request, 'core/start_page.html' )




