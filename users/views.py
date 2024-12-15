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
from django.db.models import Q
from django.conf import settings
import requests
from http.client import RemoteDisconnected

# User Registration View
def register(request):
    """
    Handles user registration and sends an email verification link.
    Redirects authenticated users to the home page.
    """
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered and logged in. Redirecting to home...')
        return redirect('home')  # Redirect to home if the user is already authenticated
    
    print("Accessing register view...") 
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User remains inactive until email verification
            user.save()

            # Create user profile
            Profile.objects.create(user=user)

            # Send the verification email
            send_verification_email(request, user)

            print(f"Verification email sent to {user.email}.") 
            messages.success(request, 'Registration successful. Please check your email to verify your account.')
            return redirect('login')
        else:
            print("Registration form is invalid:", form.errors) 
            messages.error(request, 'There was an error with your registration. Please try again.')
    else:
        form = UserRegisterForm()

    print("Passing form to template.") 
    return render(request, 'users/register.html', {'form': form})


def email_verification(request, token):
    """
    Verifies a user's email using the token provided in the verification email.
    """
    try:
        profile = get_object_or_404(Profile, verification_token=token)
        profile.user.is_active = True  # Activate the user
        profile.user.save()
        profile.email_verified = True  # Mark the email as verified
        profile.verification_token = ""  # Clear the token once used
        profile.save()
        messages.success(request, 'Your email has been verified successfully. You can now log in.')
        return redirect('login')
    except Exception as e:
        print(f"Verification failed: {e}")
        messages.error(request, 'Invalid or expired verification token. Please try again.')
        return redirect('register')

def login_view(request):
    """
    Handles user login, prevents an unverified user or an already authenticated user from logging in.
    """
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered and logged in. Redirecting to home...')
        return redirect('home')  # Redirect to home if the user is already authenticated
    
    print("Accessing login view...") 
    form = UserLoginForm(data=request.POST or None)

    if request.method == "POST":
        try:
            if form.is_valid():  # Validates all fields, including the reCAPTCHA
                username_or_email = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                try:
                    # Find user by username or email
                    user_obj = User.objects.get(
                        Q(username=username_or_email) | Q(email=username_or_email)
                    )
                    # Check if the user is inactive (not verified)
                    if not user_obj.is_active:
                        messages.error(request, 'Your account is inactive. Please verify your email to log in.')
                        return redirect('login')

                    # Authenticate the user
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

                if user:
                    # Log in the user
                    login(request, user)
                    messages.success(request, 'You have successfully logged in!')
                    return redirect('home')  # Redirect to a home/dashboard page
                else:
                    messages.error(request, 'Invalid credentials. Please try again.')
            else:
                # Handle invalid form submission
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)

        except RemoteDisconnected:
            # Handle RemoteDisconnected exception gracefully
            print("RemoteDisconnected error occurred during login.")
            messages.error(
                request,
                "There was a connection issue while processing your request. Please try again."
            )
            return redirect('login')  # Redirect to the login page

        except Exception as e:
            # Catch any other unexpected exceptions
            print(f"Unexpected error: {e}")
            messages.error(
                request,
                "An unexpected error occurred. Please try again or contact support."
            )
            return redirect('login')  # Redirect to the login page

    return render(request, 'users/login.html', {'form': form})



def verify_otp(request):
    """Handle OTP verification"""
    print("Accessing OTP verification view...")  
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        try:
            otp = OTP.objects.get(user=request.user, otp=otp_code, is_verified=False)
            print(f"Attempting OTP verification for {request.user.username}.")  

            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                print(f"OTP expired for {request.user.username}.")  
                return redirect('login')  # Optionally, redirect to login page or retry OTP

            otp.is_verified = True
            otp.save()
            messages.success(request, 'OTP verified successfully.')
            print(f"OTP verified successfully for {request.user.username}.")  
            return redirect('home')  # Redirect to home or dashboard after successful verification

        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP')
            print(f"Invalid OTP entered for {request.user.username}.")  

    print("Passing OTP verification form to template.")  
    return render(request, 'users/verify_otp.html')


def resend_otp(request):
    """Handle resending OTP if the current OTP has expired"""
    print("Accessing resend OTP view...")  
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
                print(f"A new OTP has been sent to {request.user.email}.")  
            else:
                messages.error(request, 'Your OTP is still valid. Please use it before requesting a new one.')
                print(f"OTP for {request.user.username} is still valid.")  
        except OTP.DoesNotExist:
            messages.error(request, 'No valid OTP found. Please request a new OTP.')
            print(f"No valid OTP found for {request.user.username}.")  

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


@login_required
def profile_view(request):
    """
    Displays the user's profile and account details. Checks if the profile exists, 
    and creates one if it doesn't. Ensures that the user's email is verified.
    """
    print(f"Accessing profile view for user {request.user.username}.")
    
     # Check if the user's email is verified
    if not request.user.profile.email_verified:
        messages.warning(request, 'Your email is not verified. Please verify your email to access your profile!')
        return redirect('email_verification_request')  # Redirect to the email verification request page
    
    # Check if the profile exists, if not, create it
    if not hasattr(request.user, 'profile'):
        # Create the profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)
        print(f"Created profile for user {request.user.username}.")
    else:
        profile = request.user.profile

    # Print user's profile details for debugging
    print(f"User profile details: {profile}")

    context = {
        'profile': profile,
    }

    return render(request, 'users/profile.html', context)


def email_verification_request(request):
    """
    Handles the process of re-sending the verification email if the user's email is not verified.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if the email exists in the system
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")
            return redirect('email_verification_request')

        # Ensure the user is registered but not verified
        if not user.profile.email_verified:
            # Generate a new verification token and send the verification email
            token = user.profile.generate_verification_token()
            send_verification_email(request, user)
            messages.success(request, 'A new verification email has been sent to your email address.')
        else:
            messages.info(request, 'Your email is already verified.')
        
        return redirect('profile')

    return render(request, 'users/email_verification_request.html')


@login_required
def edit_profile(request):
    """
    Allows the user to edit their profile information.
    """
    profile = get_object_or_404(Profile, user=request.user)

    # Debugging print statement for when the profile is fetched
    print(f"Accessing edit profile for user {request.user.username}. Profile: {profile}")

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        # Print form data for debugging
        print(f"Form data: {request.POST}")
        print(f"Form files: {request.FILES}")
        
        if form.is_valid():
            form.save()
            # Print success message for debugging
            print(f"Profile updated for user {request.user.username}.")
            return redirect('profile')  # Redirect to the profile page after saving
        else:
            # Print form validation errors
            print(f"Form is invalid. Errors: {form.errors}")
    else:
        form = ProfileUpdateForm(instance=profile)

    # Print the form instance for debugging
    print(f"Rendering form for user {request.user.username}. Form instance: {form}")

    return render(request, 'users/edit_profile.html', {'form': form})



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
