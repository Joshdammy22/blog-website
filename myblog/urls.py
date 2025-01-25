from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from allauth.socialaccount.providers.github.urls import urlpatterns as github_urlpatterns
from django.conf.urls import handler400, handler403, handler404, handler500

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

# Assign custom error handlers
handler400 = views.custom_400_error
handler403 = views.custom_403_error
handler404 = views.custom_404_error
handler500 = views.custom_500_error