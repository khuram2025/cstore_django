from django.urls import path

from . import api_views

urlpatterns = [
    # ... other URL patterns ...
    path('api/customers/', api_views.CustomerListView.as_view(), name='customer-list'),
    path('api/customer-create-link/', api_views.CustomerCreateLinkView.as_view(), name='customer-create-link'),
    path('api/add-transaction/', api_views.AddTransactionAPIView.as_view(), name='add-transaction'),
    path('api/customer-accounts/', api_views.CustomerAccountListView.as_view(), name='customer-account-list'),


   
]
