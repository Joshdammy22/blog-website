from django.contrib import admin
from .models import Blog, Tag, Category, Comment, Reaction, Follow, Notification

# Tag Admin
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ['name']

admin.site.register(Tag, TagAdmin)

# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ['name']

admin.site.register(Category, CategoryAdmin)

# Blog Admin
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'read_count', 'created_at', 'modified_at')
    list_filter = ('status', 'author', 'categories')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    filter_horizontal = ('tags', 'categories')
    readonly_fields = ('read_count',)  # Prevent modification of read_count

admin.site.register(Blog, BlogAdmin)

# Reaction Admin
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'blog__title')

admin.site.register(Reaction, ReactionAdmin)

# Comment Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'author', 'content', 'created_at')
    list_filter = ('created_at', 'blog', 'author')
    search_fields = ('content',)

admin.site.register(Comment, CommentAdmin)

# Follow Admin
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followee', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'followee__username')

admin.site.register(Follow, FollowAdmin)

# Notification Admin
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'notification_type')

admin.site.register(Notification, NotificationAdmin)
