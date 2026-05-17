from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'preferred_barber', 'birthday', 'created_at')
    list_filter = ('preferred_barber', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__phone')
    raw_id_fields = ('user', 'preferred_barber')
