from django.contrib import admin
from .models import Blog

class BlogAdmin(admin.ModelAdmin):
    list_display =('title', 'slug', 'created_at', 'status')
    list_filter = ('status',)
    search_field = ['title','contents']
    prepopulated_field = {'slug': ('title',)}

admin.site.register(Blog, BlogAdmin)