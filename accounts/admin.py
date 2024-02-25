from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Business

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['mobile', 'name', 'business_name', 'is_active', 'is_staff']
    search_fields = ('mobile', 'name', 'business_name')
    ordering = ('mobile',)

    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('name', 'business_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'categories']
    search_fields = ['name']

