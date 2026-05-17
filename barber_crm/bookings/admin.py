from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'barber', 'service', 'start_at', 'duration_minutes', 'status')
    list_filter = ('status', 'barber', 'service', 'start_at')
    search_fields = ('client__user__username', 'client__user__first_name', 'client__user__last_name', 'barber__user__username')
    date_hierarchy = 'start_at'
    raw_id_fields = ('client', 'barber', 'service')
