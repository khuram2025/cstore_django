from django.contrib import admin
from .models import Customer, CustomerAccount

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'display_businesses')
    
    def display_businesses(self, obj):
        return ", ".join([business.name for business in obj.businesses.all()])
    display_businesses.short_description = 'Businesses'

admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerAccount)


from django.contrib import admin
from .models import Transaction  # Adjust the import path as necessary

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('customer_account', 'date', 'time', 'amount', 'transaction_type', 'notes')
    list_filter = ('date', 'transaction_type', 'customer_account')
    search_fields = ('customer_account__customer__name', 'notes', 'amount')

admin.site.register(Transaction, TransactionAdmin)
