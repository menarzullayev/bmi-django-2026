from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'address', 'total_spent', 'created_at')
    search_fields = ('full_name', 'phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
