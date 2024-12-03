from django.urls import path
from . import views


urlpatterns = [
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('create/', views.create_blog, name='create_blog'),
    path('blogs', views.blog_list, name='blog_list'),
    path('like/<slug:slug>/', views.like_blog, name='like_blog'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),

    # Other URLs...
]