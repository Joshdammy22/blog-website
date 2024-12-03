from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
from django.utils.timezone import now
from .utils import send_verification_email, request_otp
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.exceptions import ValidationError


# User Registration View
def register(request):
    """
    Handles user registration and sends an email verification link.
    """
    print("Accessing register view...")  # Debugging
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            send_verification_email(request, user)

            print(f"Verification email sent to {user.email}.")
            messages.success(request, 'Registration successful. Please check your email to verify your account.')
            return redirect('login')
        else:
            print("Registration form is invalid:", form.errors)  # Debugging
    else:
        form = UserRegisterForm()
    print("Passing form to template.")  # Debugging
    return render(request, 'users/register.html', {'form': form})



# User Login View
def login_view(request):
    """Handle login and MFA OTP generation"""
    form = UserLoginForm(request.POST or None)
    print("Login form initialized:", form)  # Debugging
    if request.method == "POST":
        # Validate the username or email and password first
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(f"Attempting login for {username_or_email}.")  
            user = authenticate(
                request, username=username_or_email, password=password
            )
            if user is not None:
                login(request, user)
                try:
                    # Request OTP after successful login
                    otp = request_otp(user)
                    # Send OTP to the user via email
                    send_mail(
                        'Your OTP Code',
                        f'Your OTP code is: {otp.otp}',
                        'noreply@example.com',
                        [user.email],
                        fail_silently=False,
                    )
                    return redirect('verify_otp')  # Redirect to OTP verification page
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('login')
            else:
                messages.error(request, 'Invalid credentials')
    print("Passing form to template.")  # Debugging
    return render(request, 'users/login.html', {'form': form})


def verify_otp(request):
    """Handle OTP verification"""
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        try:
            otp = OTP.objects.get(user=request.user, otp=otp_code, is_verified=False)

            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('login')  # Optionally, redirect to login page or retry OTP

            otp.is_verified = True
            otp.save()
            return redirect('home')  # Redirect to home or dashboard after successful verification

        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP')

    return render(request, 'users/verify_otp.html')

def resend_otp(request):
    """Handle resending OTP if the current OTP has expired"""
    if request.method == "POST":
        try:
            otp = OTP.objects.get(user=request.user, is_verified=False)

            if otp.is_expired():
                # Generate a new OTP
                otp.generate_otp()
                otp.save()

                # Send new OTP to the user via email
                send_mail(
                    'Your New OTP Code',
                    f'Your new OTP code is: {otp.otp}',
                    'noreply@example.com',
                    [request.user.email],
                    fail_silently=False,
                )
                messages.success(request, 'A new OTP has been sent to your email.')
            else:
                messages.error(request, 'Your OTP is still valid. Please use it before requesting a new one.')
        except OTP.DoesNotExist:
            messages.error(request, 'No valid OTP found. Please request a new OTP.')

    return redirect('verify_otp')  # Redirect to OTP verification page


# User Logout View
@login_required
def logout_view(request):
    """
    Logs out the currently logged-in user and redirects to the home page.
    """
    print(f"Logging out user {request.user.username}.") 
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')  


# User Profile View
@login_required
def profile_view(request):
    """
    Displays and updates the user's profile and account details.
    """
    print(f"Accessing profile view for user {request.user.username}.") 
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            print(f"Profile updated for user {request.user.username}.") 
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
        else:
            print("Profile update form is invalid.") 
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/profile.html', context)


# User Settings View
@login_required
def settings_view(request):
    """
    Manages user settings such as email notifications and dark mode preferences.
    """
    print(f"Accessing settings view for user {request.user.username}.") 
    settings = get_object_or_404(UserSettings, user=request.user)
    if request.method == 'POST':
        email_notifications = request.POST.get('email_notifications') == 'on'
        dark_mode = request.POST.get('dark_mode') == 'on'
        settings.email_notifications = email_notifications
        settings.dark_mode = dark_mode
        settings.save()
        print(f"Settings updated for user {request.user.username}.") 
        messages.success(request, 'Your settings have been updated.')
        return redirect('settings')
    return render(request, 'users/settings.html', {'settings': settings})


# User Blog Interaction View
@login_required
def user_blog_interactions(request):
    """
    Displays all blogs that the user has interacted with (liked, commented, etc.).
    """
    print(f"Fetching blog interactions for user {request.user.username}.") 
    interactions = UserBlogInteraction.objects.filter(user=request.user)
    print(f"Found {interactions.count()} interactions for user {request.user.username}.") 
    return render(request, 'users/blog_interactions.html', {'interactions': interactions})
