from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'amount', 'method', 'paid_at', 'cashier')
    list_filter = ('method', 'paid_at')
    search_fields = ('ticket__ticket_number',)
    date_hierarchy = 'paid_at'
