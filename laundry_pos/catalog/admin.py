from django.contrib import admin
from .models import ClothType, ServiceType, PriceRule


@admin.register(ClothType)
class ClothTypeAdmin(admin.ModelAdmin):
    list_display = ('default_icon', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}


@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):
    list_display = ('cloth_type', 'service_type', 'price')
    list_filter = ('service_type', 'cloth_type__category')
    list_editable = ('price',)
    search_fields = ('cloth_type__name', 'service_type__name')
