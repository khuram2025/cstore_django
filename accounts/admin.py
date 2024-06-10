from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Business
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('mobile', 'name', 'business_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('name', 'business_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2', 'name', 'business_name', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('mobile', 'name', 'business_name')
    ordering = ('mobile',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(CustomUser, CustomUserAdmin)

class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'categories')
    search_fields = ('name', 'user__mobile', 'categories')
    list_filter = ('user',)

admin.site.register(Business, BusinessAdmin)
