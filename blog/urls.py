from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_blog, name='create_blog'),
    path('', views.blog_list, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('<slug:slug>/like/', views.like_blog, name='like_blog'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
]
