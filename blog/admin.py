from django.contrib import admin
from .models import Tag, Category, Blog, Reaction, Comment, Follow, Notification

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'modified_at', 'featured')
    list_filter = ('status', 'featured', 'created_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags', 'categories')
    
    def get_reaction_summary(self, obj):
        return obj.get_reaction_summary()
    
    get_reaction_summary.short_description = 'Reactions Summary'

class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('blog__title', 'user__username')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'blog', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'blog__title')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followee', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'followee__username')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'notification_type')

# Register models in the admin panel
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Reaction, ReactionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Notification, NotificationAdmin)
