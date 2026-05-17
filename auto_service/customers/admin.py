from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'company', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone', 'company', 'email')
    date_hierarchy = 'created_at'
    ordering = ('name',)
