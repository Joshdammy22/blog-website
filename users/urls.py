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
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html', email_template_name='users/password_reset_email.html',), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),


    # User Logout
    path('logout/', views.logout_view, name='logout'),

    # User Profile
    path('profile/', views.profile_view, name='profile'),
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

