from django.contrib import admin
from .models import Profile, UserActivity, UserBlogInteraction, UserSettings


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'phone_number', 'birth_date')
    search_fields = ('user__username', 'location', 'phone_number')
    list_filter = ('location',)
    ordering = ('user__username',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login_time', 'last_activity_time')
    search_fields = ('user__username',)
    list_filter = ('last_login_time', 'last_activity_time')
    ordering = ('-last_activity_time',)


@admin.register(UserBlogInteraction)
class UserBlogInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'is_favorite', 'liked', 'commented', 'last_interaction')
    search_fields = ('user__username', 'blog__title')
    list_filter = ('is_favorite', 'liked', 'commented', 'last_interaction')
    ordering = ('-last_interaction',)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'dark_mode')
    search_fields = ('user__username',)
    list_filter = ('email_notifications', 'dark_mode')
    ordering = ('user__username',)
