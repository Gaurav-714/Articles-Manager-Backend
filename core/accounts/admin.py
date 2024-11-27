from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserModel, AccountVerificationOTP

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'has_approval')}),
        ('Timestamps', {'fields': ('createdAt', 'updatedAt')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password'),
        }),
    )
    readonly_fields = ('createdAt', 'updatedAt')
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'createdAt', 'updatedAt')
    list_filter = ('is_staff', 'is_active', 'has_approval')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(UserModel, UserAdmin)
admin.site.register(AccountVerificationOTP)

