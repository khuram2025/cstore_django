from django.contrib import admin
from .models import Customer, CustomerAccount

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'display_businesses')
    
    def display_businesses(self, obj):
        return ", ".join([business.name for business in obj.businesses.all()])
    display_businesses.short_description = 'Businesses'

admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerAccount)
