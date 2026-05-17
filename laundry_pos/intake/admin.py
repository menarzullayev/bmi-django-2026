from django.contrib import admin
from .models import IntakeTicket, Garment
from payments.models import Payment


class GarmentInline(admin.TabularInline):
    model = Garment
    extra = 0
    verbose_name = 'Вещь'
    verbose_name_plural = 'Вещи'


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    verbose_name = 'Оплата'
    verbose_name_plural = 'Оплаты'
    readonly_fields = ('paid_at',)


@admin.register(IntakeTicket)
class IntakeTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'customer', 'status', 'received_at', 'total', 'amount_paid', 'cashier')
    list_filter = ('status', 'pickup_method', 'received_at')
    search_fields = ('ticket_number', 'customer__full_name', 'customer__phone')
    readonly_fields = ('ticket_number', 'qr_image', 'subtotal', 'total')
    inlines = [GarmentInline, PaymentInline]
    date_hierarchy = 'received_at'


@admin.register(Garment)
class GarmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'cloth_type', 'service_type', 'price', 'status')
    list_filter = ('status', 'service_type', 'cloth_type')
    search_fields = ('ticket__ticket_number',)
