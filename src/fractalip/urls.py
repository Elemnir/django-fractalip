from django.urls    import path

from .views import (NetworkCreateView, NetworkDetailView, NetworkListView,
                    AddressBlockCreateView, AddressBlockDeleteView,
                    AddressBlockLookupView, AddressBlockUpdateView,
                    AddressPingCheckView, AddressUpdateView)

app_name = "fractalip"

urlpatterns = [
    path('', NetworkListView.as_view(), name='network-list'),
    path('create/', NetworkCreateView.as_view(), name='network-create'),
    path('view/<int:pk>/', NetworkDetailView.as_view(), name='network-detail'),
    path('block/create/', AddressBlockCreateView.as_view(), name='block-create'),
    path('block/delete/<int:pk>/', AddressBlockDeleteView.as_view(), name='block-delete'),
    path('block/scan/<int:pk>/', AddressBlockLookupView.as_view(), name='block-lookup'),
    path('block/<int:pk>/', AddressBlockUpdateView.as_view(), name='block-update'),
    path('address/ping/<int:pk>/', AddressPingCheckView.as_view(), name='address-ping'),
    path('address/<int:pk>/', AddressUpdateView.as_view(), name='address-update'),
]
