from django.urls import path

from . import api_views

urlpatterns = [
    # ... other URL patterns ...
    path('api/customers/', api_views.CustomerListView.as_view(), name='customer-list'),
    path('api/customer-create-link/', api_views.CustomerCreateLinkView.as_view(), name='customer-create-link'),
   
]
