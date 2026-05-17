from django.contrib import admin

from .models import ServiceTask


@admin.register(ServiceTask)
class ServiceTaskAdmin(admin.ModelAdmin):
    list_display = (
        'description', 'workorder', 'mechanic',
        'status', 'estimated_hours', 'actual_hours',
    )
    list_filter = ('status', 'mechanic')
    search_fields = ('description', 'workorder__order_number')
