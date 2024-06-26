from django.urls import path

from . import api_views

urlpatterns = [
    # ... other URL patterns ...
    
    path('api/customer-create-link/', api_views.CustomerCreateLinkView.as_view(), name='customer-create-link'),
    path('api/add-transaction/', api_views.AddTransactionView.as_view(), name='add-transaction'),
    path('api/transactions/<int:customer_account_id>/', api_views.TransactionListView.as_view(), name='transaction-list'),
    path('api/transaction/<int:transaction_id>/', api_views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('api/customer-accounts/', api_views.CustomerAccountListView.as_view(), name='customer-account-list'),  
    path('api/customer-accounts/edit/<int:account_id>/', api_views.CustomerAccountEditProfileView.as_view(), name='customer-account-edit'),

]






