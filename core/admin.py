from django.contrib import admin
from .models import Config, Setting


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['method', 'api_url_short', 'is_active', 'created_at']
    list_filter = ['method', 'is_active', 'created_at']
    search_fields = ['api_url', 'data']
    list_editable = ['is_active']

    def api_url_short(self, obj):
        return obj.api_url[:50] + '...' if len(obj.api_url) > 50 else obj.api_url
    api_url_short.short_description = 'API URL'


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_short', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'value']
    list_editable = ['is_active']

    def value_short(self, obj):
        if obj.value:
            return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
        return '-'
    value_short.short_description = 'Value'
