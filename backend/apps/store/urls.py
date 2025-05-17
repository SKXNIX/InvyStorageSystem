from django.urls import path
from django.contrib.auth.decorators import login_required
import apps.store.views as views

app_name = 'store'

urlpatterns = [
    path('', views.store_page, name='store-settings'),    # Панель управления складом

    path('places/', views.PlaceListView.as_view(), name='place-list'),
    path('places/<int:pk>/', views.PlaceDetailView.as_view(), name='place-detail'),
    path('places/create', views.PlaceCreateView.as_view(), name='place-create'),
    path('places/<int:pk>/update/', views.PlaceUpdateView.as_view(), name='place-update'),
    path('places/<int:pk>/delete/', views.PlaceDeleteView.as_view(), name='place-delete'),
    path('delete-selected-places/', views.DeleteSelectedPlaceView.as_view(), name='delete-selected-places'),



    path('add-receipt/', views.add_stock_receipt, name='add-receipt'),
    path('receipt-list/', views.ReceiptListView.as_view(), name='receipts-list'),
    path('receipt-list/<int:pk>/update-status/', views.update_receipt_status, name='update_receipt_status'),
    path('delete-selected-receipts/', views.DeleteSelectedReceiptsView.as_view(), name='delete-selected-receipts'),

    path('add-dispatch/', views.add_dispatch, name='add-dispatch'),
    path('dispatch-list/', views.DispatchListView.as_view(), name='dispatch-list'),
    path('dispatch-list/<int:pk>/update-status/', views.update_dispatch_status, name='update-dispatch-status'),
    path('delete-selected-dispatches/', views.DeleteSelectedDispatchesView.as_view(), name='delete-selected-dispatches'),

    path('storage/', views.store_list, name='store-list'),

    path('add-supplier/', views.add_supplier, name='add-supplier'),
    path('suppliers-list/', views.SupplierListView.as_view(), name='suppliers-list'),
    path('suppliers-list/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers-list/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier-update'),
    path('delete-selected-suppliers/', views.DeleteSelectedSuppliersView.as_view(), name='delete-selected-suppliers'),


    
]