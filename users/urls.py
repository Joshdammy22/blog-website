from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # User Registration
    path('register/', views.register, name='register'),
    path('email-sent/<str:email>/', views.email_sent, name='email_sent'),
    path('resend-verification/<str:email>/', views.resend_verification_email, name='resend_verification_email'),
    path('verify/<str:token>/', views.email_verification, name='email_verification'),
    

    path('login/', views.login_view, name='login'),  # Login view
    path('verify-otp/', views.verify_otp, name='verify_otp'),  # OTP verification view
    path('resend-otp/', views.resend_otp, name='resend_otp'),  # Resend OTP view


    # Password reset URLs
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),


    # User Logout
    path('logout/', views.logout_view, name='logout'),

    # User Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.author_profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),

    path('email-verification-request/', views.email_verification_request, name='email_verification_request'),


    # User Settings
    path('settings/', views.settings_view, name='settings'),

    # User Blog Interactions
    path('blog-interactions/', views.user_blog_interactions, name='blog_interactions'),

    # OTP Verification
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # Resend OTP
    path('resend-otp/', views.resend_otp, name='resend_otp'),

    path('notifications/', views.notifications, name='notifications'),
    path('my-blogs/', views.my_blogs, name='my_blogs'),
    path('recent-activities/', views.recent_activities, name='recent_activities'),

    path('change-email/', views.change_email, name='change_email'), 

    
]

