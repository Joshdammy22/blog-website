"""
URL configuration for myblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),  # Default admin login and dashboard

    # Home page
    path('', views.home, name='home'),

    # Blog app URLs
    path('blogs/', include('blog.urls')),

    # User app URLs
    path('user/', include('users.urls')),

    path('accounts/', include('allauth.urls')), 
]
if settings.DEBUG:
    # For static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # For media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
