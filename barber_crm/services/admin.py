from django.contrib import admin
from .models import Service, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_emoji', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
