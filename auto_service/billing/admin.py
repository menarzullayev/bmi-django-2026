from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'workorder', 'subtotal',
        'tax_amount', 'total', 'issued_at', 'paid_at',
    )
    list_filter = ('payment_method', 'issued_at', 'paid_at')
    search_fields = ('invoice_number', 'workorder__order_number')
    date_hierarchy = 'issued_at'
