from django.contrib import admin
from .models import Follow, Comment, Blog, Notification, Tag

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'created_at', 'status')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}  # Corrected field name
    ordering = ('-created_at',)
    autocomplete_fields = ('tags',)  # Added for easier tag selection in admin

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'author', 'created_at', 'content_summary')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'blog__title')

    def content_summary(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_summary.short_description = 'Comment Content'

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followee', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'followee__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'notification_type')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
