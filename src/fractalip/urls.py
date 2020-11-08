from django.urls    import path

from .views import (NetworkCreateView, NetworkDetailView, NetworkListView,
                    AddressBlockCreateView, AddressBlockDeleteView, 
                    AddressBlockUpdateView, AddressUpdateView)

app_name = "fractalip"

urlpatterns = [
    path('', NetworkListView.as_view(), name='network-list'),
    path('create/', NetworkCreateView.as_view(), name='network-create'),
    path('view/<int:pk>/', NetworkDetailView.as_view(), name='network-detail'),
    path('block/create/', AddressBlockCreateView.as_view(), name='block-create'),
    path('block/delete/<int:pk>/', AddressBlockDeleteView.as_view(), name='block-delete'),
    path('block/<int:pk>/', AddressBlockUpdateView.as_view(), name='block-update'),
    path('address/<int:pk>/', AddressUpdateView.as_view(), name='address-update'),
]
