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
    
]