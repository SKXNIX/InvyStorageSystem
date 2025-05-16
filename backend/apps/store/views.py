from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.custom_auth.models import CustomUser
from apps.core.mixins import RoleRequiredMixin
from apps.core.decorators import role_required
from apps.store.models import Place


class PlaceListView(RoleRequiredMixin, ListView):
    model = Place
    allowed_roles = ['superadmin', 'admin']
    template_name = 'store/place_list.html'
    context_object_name = 'places'

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


class PlaceDetailView(RoleRequiredMixin, DetailView):
    model = Place
    allowed_roles = ['superadmin', 'admin']
    template_name = 'store/place_detail.html'

class PlaceCreateView(RoleRequiredMixin, CreateView):
    model = Place
    allowed_roles = ['superadmin', 'admin']
    fields = ['name', 'parent', 'identifier', 'type', 'capacity', 'temperature']
    template_name = 'store/place_form.html'
    success_url = '/store/places/'

class PlaceUpdateView(RoleRequiredMixin, UpdateView):
    model = Place
    allowed_roles = ['superadmin', 'admin']
    fields = ['name', 'parent', 'identifier', 'type', 'capacity', 'temperature']
    template_name = 'store/place_form.html'
    success_url = '/store/places/'

class PlaceDeleteView(RoleRequiredMixin, DeleteView):
    model = Place
    allowed_roles = ['superadmin', 'admin']
    template_name = 'store/place_confirm_delete.html'
    success_url = '/store/places/'

class DeleteSelectedPlaceView(RoleRequiredMixin, FormView):
    allowed_roles = ['superadmin', 'admin']

    def post(self, request):
        selected_places = request.POST.getlist('selected_places')
        if selected_places:
            selected_places = list(map(int, selected_places))
            Place.objects.filter(id__in=selected_places).delete()
            messages.success(request, "Выбранные места удалены")
        else:
            messages.warning(request, "Нет выбранных мест")
        return HttpResponseRedirect(reverse_lazy('store:place-list'))

@role_required(['superadmin','admin'])
def store_page(request):
    """"""
    return render(request, 'store/index.html')