from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ('username', 'phone', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'phone', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'role', 'avatar')}),
    )
    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'role')}),
    )


admin.site.site_header = 'Барбершоп — Администрирование'
admin.site.site_title = 'Барбершоп CRM'
admin.site.index_title = 'Панель управления'
