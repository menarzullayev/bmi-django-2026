from django.contrib import admin

from .models import PartCategory, PartUsage, SparePart


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'sku', 'category', 'brand',
        'quantity_in_stock', 'reorder_level', 'unit_price',
    )
    list_filter = ('category', 'brand')
    search_fields = ('name', 'sku', 'brand')
    autocomplete_fields = ('category',)
    ordering = ('name',)


@admin.register(PartUsage)
class PartUsageAdmin(admin.ModelAdmin):
    list_display = ('part', 'workorder', 'quantity', 'unit_price', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('part__name', 'part__sku', 'workorder__order_number')
    date_hierarchy = 'used_at'
