from django.contrib import admin
from .models import DeliveryRoute, DeliveryAssignment


class DeliveryAssignmentInline(admin.TabularInline):
    model = DeliveryAssignment
    extra = 0


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ('date', 'driver', 'status')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'
    inlines = [DeliveryAssignmentInline]


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('route', 'ticket', 'address', 'order', 'status', 'delivered_at')
    list_filter = ('status',)
    search_fields = ('ticket__ticket_number', 'address')
