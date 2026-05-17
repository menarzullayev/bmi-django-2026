from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Профиль химчистки', {'fields': ('role', 'phone', 'full_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Профиль химчистки', {'fields': ('role', 'phone', 'full_name')}),
    )
