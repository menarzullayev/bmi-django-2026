from django.contrib import admin
from .models import Barber


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'experience_years', 'rating', 'is_active')
    list_filter = ('is_active', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')
    raw_id_fields = ('user',)
