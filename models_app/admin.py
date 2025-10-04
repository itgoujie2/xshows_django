from django.contrib import admin
from .models import WebcamModel, ModelCategory, Favourite, XLoveCashTag, Subscription, Notification


@admin.register(WebcamModel)
class WebcamModelAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user_name', 'source', 'is_online', 'is_naked', 'gender', 'age', 'created_at']
    list_filter = ['source', 'is_online', 'is_naked', 'gender', 'created_at']
    search_fields = ['display_name', 'user_name', 'model_id', 'description']
    list_editable = ['is_online']
    readonly_fields = ['created_at', 'updated_at', 'nudity_last_check', 'nudity_image_hash']

    fieldsets = (
        ('Basic Information', {
            'fields': ('model_id', 'user_name', 'unique_user_name', 'display_name', 'source')
        }),
        ('Details', {
            'fields': ('age', 'gender', 'description', 'is_online')
        }),
        ('Nudity Detection', {
            'fields': ('is_naked', 'nudity_confidence', 'nudity_last_check', 'nudity_image_hash')
        }),
        ('Media & Links', {
            'fields': ('image', 'iframe', 'link_embed', 'link_snapshot', 'url_stream', 'chat_url')
        }),
        ('Data', {
            'fields': ('json_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ModelCategory)
class ModelCategoryAdmin(admin.ModelAdmin):
    list_display = ['model', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['model__display_name', 'category__name']


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'model', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'model__display_name']


@admin.register(XLoveCashTag)
class XLoveCashTagAdmin(admin.ModelAdmin):
    list_display = ['tag', 'created_at']
    search_fields = ['tag']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'model', 'is_active', 'notification_method', 'last_notified_at', 'created_at']
    list_filter = ['is_active', 'notification_method', 'created_at']
    search_fields = ['user__username', 'user__email', 'model__display_name', 'model__user_name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'model', 'is_active', 'notification_method')
        }),
        ('Notification History', {
            'fields': ('last_notified_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscription', 'model', 'notification_type', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'notification_type', 'created_at', 'sent_at']
    search_fields = ['subscription__user__username', 'model__display_name', 'error_message']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Notification Details', {
            'fields': ('subscription', 'model', 'notification_type', 'status')
        }),
        ('Delivery Information', {
            'fields': ('sent_at', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
