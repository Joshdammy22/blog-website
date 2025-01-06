from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'phone_number', 'birth_date')
    search_fields = ('user__username', 'location', 'phone_number')
    list_filter = ('location',)
    ordering = ('user__username',)



