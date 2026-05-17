from django.contrib import admin
from .models import QueueEntry


@admin.register(QueueEntry)
class QueueEntryAdmin(admin.ModelAdmin):
    list_display = ('client', 'preferred_barber', 'status', 'served_by', 'joined_at')
    list_filter = ('status', 'preferred_barber')
    search_fields = ('client__user__username', 'client__user__first_name', 'client__user__last_name')
    raw_id_fields = ('client', 'preferred_barber', 'served_by')
