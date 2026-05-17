from django.contrib import admin

from parts.models import PartUsage
from workflow.models import ServiceTask

from .models import WorkOrder


class ServiceTaskInline(admin.TabularInline):
    model = ServiceTask
    extra = 0
    fields = ('description', 'mechanic', 'status', 'estimated_hours', 'actual_hours', 'hourly_rate', 'order')


class PartUsageInline(admin.TabularInline):
    model = PartUsage
    extra = 0
    fields = ('part', 'quantity', 'unit_price', 'used_at')
    readonly_fields = ('used_at',)


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'vehicle', 'assigned_mechanic',
        'status', 'priority', 'received_at',
    )
    list_filter = ('status', 'priority', 'assigned_mechanic')
    search_fields = ('order_number', 'vehicle__plate', 'vehicle__customer__name')
    date_hierarchy = 'received_at'
    inlines = [ServiceTaskInline, PartUsageInline]
    autocomplete_fields = ('vehicle',)
