from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from allauth.socialaccount.providers.github.urls import urlpatterns as github_urlpatterns


urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),  # Default admin login and dashboard

    # Home page
    path('', views.home, name='home'),
    path('verify_email/', views.verify_email, name='verify_email'),

    # Blog app URLs
    path('blogs/', include('blog.urls')),

    # User app URLs
    path('users/', include('users.urls')),

    path('accounts/', include('allauth.urls')), 
    path('accounts/social/debug/', include('allauth.socialaccount.urls')),

]+ github_urlpatterns

if settings.DEBUG:
    # For static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # For media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
