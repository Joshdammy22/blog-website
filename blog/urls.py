from django.urls import path
from . import views


urlpatterns = [
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/save_reaction/', views.save_reaction, name='save_reaction'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('mark-as-read/<slug:slug>/', views.mark_as_read, name='mark_as_read'),

    
    path('create/', views.create_blog, name='create_blog'),
    path('blog/update/<slug:slug>/', views.update_blog, name='update_blog'),
    path('delete/<slug:slug>/', views.delete_blog, name='delete_blog'),


    
    path('blogs', views.blog_list, name='blogs'),


    #path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),

    # Other URLs...
    path('toggle-follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),

]