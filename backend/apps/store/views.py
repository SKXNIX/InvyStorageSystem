from math import e
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from apps.custom_auth.models import CustomUser
from apps.core.mixins import RoleRequiredMixin
from apps.core.decorators import role_required

from apps.store.models import Dispatch, Place, StockReceipt, Store, Supplier
from apps.store.forms import StockDispatchStatusForm, StockReceiptForm, StockReceiptStatusForm, SupplierForm, StockDispatchForm


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


class DeleteSelectedReceiptsView(RoleRequiredMixin, FormView):
    allowed_roles = ['superadmin', 'admin']

    def post(self, request):
        selected_receipts = request.POST.getlist('selected_receipts')
        if selected_receipts:
            selected_receipts = list(map(int, selected_receipts))
            StockReceipt.objects.filter(id__in=selected_receipts).delete()
            messages.success(request, "Выбранные поступления удалены")
        else:
            messages.warning(request, "Нет выбранных поступлений")
        return HttpResponseRedirect(reverse_lazy('store:receipts-list'))


@login_required
@role_required(['superadmin','admin','storekeeper'])
def store_page(request):
    """"""
    return render(request, 'store/index.html')

@login_required
@role_required(['superadmin', 'admin','storekeeper'])
def add_stock_receipt(request):
    if request.method == 'POST':
        form = StockReceiptForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('store:receipts-list')
    else:
        form = StockReceiptForm(user=request.user)

    return render(request, 'store/add_receipt.html', {'form': form})


class ReceiptListView(RoleRequiredMixin, ListView):
    """Представление: список поступлений"""
    model = StockReceipt
    template_name = 'store/receipt_list.html'
    allowed_roles = ['superadmin', 'admin','storekeeper']
    context_object_name = 'receipts'

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

@login_required
@role_required(['superadmin', 'admin','storekeeper'])
def update_receipt_status(request, pk):
    receipt = get_object_or_404(StockReceipt, pk=pk)
    if request.method == 'POST':
        form = StockReceiptStatusForm(request.POST, instance=receipt)
        if form.is_valid():
            try:
                new_status = form.cleaned_data['status']
                original_status = receipt.status
                receipt.status = new_status
                if original_status == 'received' and new_status != 'received':
                    if not request.user.role == 'superadmin':
                        messages.error(request, "Только суперадмин может отменить статус")
                        return render(request, 'store/update_receipt_status.html', 
                                      {'form': form, 'receipt': receipt})
                form.save()
                return redirect('store:receipts-list')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Форма содержит ошибки" + str(form.errors))
    else:
        form = StockReceiptForm(instance=receipt, user=request.user)
    return render(request, 'store/update_receipt_status.html', {'form': form, 'receipt': receipt})



class SupplierListView(RoleRequiredMixin, ListView):
    """Представление: список поставщиков"""
    model = Supplier
    template_name = 'store/suppliers_list.html'
    allowed_roles = ['superadmin', 'admin','storekeeper']
    context_object_name = 'suppliers'

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

@login_required
@role_required(['superadmin', 'admin'])
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:suppliers-list')
    else:
        form = SupplierForm(request.POST)
    
    return render(request, 'store/supplier_form.html', {'form': form})

@login_required
@role_required(['superadmin', 'admin'])
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        return redirect('store:suppliers-list')
    return render(request, 'store/supplier_update.html', {'supplier': supplier})

@login_required
@role_required(['superadmin', 'admin', 'storekeeper'])
def add_dispatch(request):
    if request.method == 'POST':
        form = StockDispatchForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('store:dispatch-list')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = StockDispatchForm()

    return render(request, 'store/add_dispatch.html', {'form': form})



class DispatchListView(RoleRequiredMixin, ListView):
    """Представление: список отгрузок"""
    model = Dispatch
    template_name = 'store/dispatch_list.html'
    allowed_roles = ['superadmin', 'admin','storekeeper']
    context_object_name = 'dispatches'

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


@login_required
@role_required(['superadmin', 'admin', 'storekeeper'])
def dispatch_list(request):
    dispatches = Dispatch.objects.all().order_by('-dispatch_date')
    return render(request, 'store/dispatch_list.html', {'dispatches': dispatches})


@login_required
@role_required(['superadmin', 'admin', 'storekeeper'])
def update_dispatch_status(request, pk):
    dispatch = get_object_or_404(Dispatch, pk=pk)
    if request.method == 'POST':
        form = StockDispatchStatusForm(request.POST, instance=dispatch)
        if form.is_valid():
            try:
                new_status = form.cleaned_data['status']
                original_status = dispatch.status
                dispatch.status = new_status
                if original_status == 'dispatched' and new_status != 'dispatched':
                    if not request.user.role == 'superadmin':
                        messages.error(request, "Только суперадмин может отменить статус")
                        return render(request, 'store/update_dispatch_status.html', 
                                      {'form': form, 'dispatch': dispatch})
                form.save()
                return redirect('store:dispatch-list')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Форма содержит ошибки" + str(form.errors))
    else:
        form = StockDispatchForm(instance=dispatch)
    return render(request, 'store/update_dispatch_status.html', {'dispatch': dispatch})

@login_required
@role_required(['superadmin', 'admin', 'storekeeper'])
def store_list(request):
    stores = Store.objects.all().order_by('product__name')
    return render(request, 'store/store_list.html', {'stores': stores})


class DeleteSelectedDispatchesView(RoleRequiredMixin, FormView):
    allowed_roles = ['superadmin', 'admin']

    def post(self, request):
        selected_dispatches = request.POST.getlist('selected_dispatches')
        if selected_dispatches:
            selected_dispatches = list(map(int, selected_dispatches))
            Dispatch.objects.filter(id__in=selected_dispatches).delete()
            messages.success(request, "Выбранные отгрузки удалены")
        else:
            messages.warning(request, "Нет выбранных отгрузок")
        return HttpResponseRedirect(reverse_lazy('store:dispatch-list'))


class DeleteSelectedSuppliersView(RoleRequiredMixin, FormView):
    allowed_roles = ['superadmin', 'admin']

    def post(self, request):
        selected_suppliers = request.POST.getlist('selected_suppliers')
        if selected_suppliers:
            selected_suppliers = list(map(int, selected_suppliers))
            try:
                Supplier.objects.filter(id__in=selected_suppliers).delete()
                messages.success(request, "Выбранные поставщики удалены")
            except Exception as e:
                messages.warning(request, "Поставщики заняты")
                return HttpResponseRedirect(reverse_lazy('store:suppliers-list'))
        else:
            messages.warning(request, "Нет выбранных поставщиков")
        return HttpResponseRedirect(reverse_lazy('store:suppliers-list'))\


class SupplierDetailView(RoleRequiredMixin, DetailView):
    model = Supplier
    allowed_roles = ['superadmin', 'admin']
    template_name = 'store/supplier_detail.html'
    context_object_name = 'supplier'
    pk_url_kwarg = 'pk'

class SupplierUpdateView(RoleRequiredMixin, UpdateView):
    model = Supplier
    allowed_roles = ['superadmin', 'admin']
    fields = '__all__'
    template_name = 'store/supplier_form.html'
    success_url = '/store/suppliers-list/'
    context_object_name = 'supplier'
    pk_url_kwarg = 'pk'