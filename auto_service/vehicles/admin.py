from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'make', 'model', 'year', 'customer', 'mileage_km')
    list_filter = ('make', 'year')
    search_fields = ('plate', 'make', 'model', 'vin', 'customer__name')
    autocomplete_fields = ('customer',)
    ordering = ('-created_at',)
