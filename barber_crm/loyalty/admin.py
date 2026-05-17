from django.contrib import admin
from .models import LoyaltyAccount, PointsTransaction


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ('client', 'balance', 'tier', 'updated_at')
    list_filter = ('tier',)
    search_fields = ('client__user__username', 'client__user__first_name', 'client__user__last_name')
    raw_id_fields = ('client',)


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('reason', 'account__client__user__username')
    raw_id_fields = ('account', 'appointment')
    date_hierarchy = 'created_at'
