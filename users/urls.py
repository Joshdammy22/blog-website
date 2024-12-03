from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Password reset URLs
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # User Registration
    path('register/', views.register, name='register'),

    # User Login
    path('login/', views.login_view, name='login'),

    # User Logout
    path('logout/', views.logout_view, name='logout'),

    # User Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),


    # User Settings
    path('settings/', views.settings_view, name='settings'),

    # User Blog Interactions
    path('blog-interactions/', views.user_blog_interactions, name='blog_interactions'),

    # OTP Verification
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # Resend OTP
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]
