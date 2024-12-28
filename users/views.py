from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
from blog.models import *
from .utils import *
from django.core.mail import send_mail
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.conf import settings
from http.client import RemoteDisconnected
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.utils.timezone import now
from datetime import datetime, timedelta


# Logger setup
logger = logging.getLogger(__name__)

def register(request):
    """
    Handles user registration and sends an email verification link.
    Redirects authenticated users to the home page.
    """
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered and logged in. Redirecting to home...')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Create a user instance but do not save yet
                user = form.save(commit=False)
                user.is_active = False  # Keep inactive until verification

                # Send the verification email
                try:
                    send_verification_email(request, user)
                    user.save()  # Save the user only after email is sent
                    messages.success(request, 'Registration successful. Please check your email to verify your account.')
                    return redirect('email_sent', email=user.email)
                except Exception as e:
                    logger.error(f"Error sending verification email: {e}")
                    messages.error(request, 'Error sending verification email. Please try again later.')
                    return redirect('register')

            except IntegrityError as e:
                logger.error(f"Integrity error during registration: {e}")
                messages.error(request, 'Username or email already exists. Please use a different one.')
            except ValidationError as e:
                logger.error(f"Validation error during registration: {e}")
                messages.error(request, 'Invalid data provided. Please correct the errors and try again.')
            except Exception as e:
                logger.error(f"Unexpected error during registration: {e}")
                messages.error(request, 'An unexpected error occurred. Please try again later.')
        else:
            # Form is invalid: handle field-specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})

def email_sent(request, email):
    """
    Displays a page asking the user to verify their email address.
    Provides an option to resend the verification email.
    """
    return render(request, "users/email_sent.html", {'email': email})


def email_verification(request, token):
    """
    Verifies a user's email using the token and updates their Profile's email_verified field
    and the User's is_active field.
    """
    email = validate_verification_token(token)
    if not email:
        messages.error(request, 'Invalid or expired verification token. Please try again.')
        return redirect('register')

    try:
        # Fetch the user by email
        user = User.objects.get(email=email)

        # Update the user's active status and profile email verification status
        user.is_active = True
        user.save()

        # Ensure the Profile exists and update email_verified
        profile, created = Profile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()

        messages.success(request, 'Your email has been verified successfully. You can now log in.')
        return redirect('login')
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        return redirect('register')
    except Exception as e:
        # Log unexpected errors for debugging
        logger.error(f"Unexpected error during email verification: {e}")
        messages.error(request, 'An unexpected error occurred. Please try again later.')
        return redirect('register')
    

def resend_verification_email(request, email):
    """
    Resends the email verification link to the given email address with rate limiting.
    """
    cache_key = f"resend_email_limit_{email}"
    max_resends = 2  # Maximum allowed resends
    time_window = timedelta(hours=1)  # Time window for the rate limit (e.g., 1 hour)

    # Retrieve rate limit data from the cache
    resend_data = cache.get(cache_key, {"count": 0, "first_attempt": now()})
    resend_count = resend_data["count"]
    first_attempt = resend_data["first_attempt"]

    # Check if the rate limit has been exceeded
    if resend_count >= max_resends and now() < first_attempt + time_window:
        messages.error(
            request,
            f"You have exceeded the maximum number of resend attempts. Please try again after "
            f"{(first_attempt + time_window - now()).seconds // 60} minutes."
        )
        return redirect("email_sent", email=email)

    # Update the cache with the new attempt
    if now() > first_attempt + time_window:
        # Reset the counter if the time window has passed
        resend_data = {"count": 1, "first_attempt": now()}
    else:
        resend_data["count"] += 1

    # Save the updated data to the cache
    cache.set(cache_key, resend_data, timeout=int(time_window.total_seconds()))

    try:
        user = User.objects.get(email=email, is_active=False)
        send_verification_email(request, user)
        messages.success(request, f"A new verification email has been sent to {email}.")
    except User.DoesNotExist:
        messages.error(request, "No inactive account found with this email address.")
    except Exception as e:
        logger.error(f"Error resending verification email: {e}")
        messages.error(request, "An error occurred while resending the email. Please try again later.")

    return redirect("email_sent", email=email)


# User Login View
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Redirecting to home...')
        return redirect('home')

    form = UserLoginForm(data=request.POST or None)

    if request.method == "POST":
        try:
            if form.is_valid():
                username_or_email = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                try:
                    user_obj = User.objects.get(
                        Q(username=username_or_email) | Q(email=username_or_email)
                    )

                    if not user_obj.is_active:
                        messages.error(request, 'Your email is unverified. Please check your inbox and verify your email.')
                        return redirect('login')

                    user = authenticate(request, username=user_obj.username, password=password)
                    if user:
                        login(request, user)
                        messages.success(request, 'You have successfully logged in!')

                        # Generate OTP and send it
                        otp = create_and_send_otp(user)

                        # Redirect to OTP verification page
                        return redirect('verify_otp')  # Redirect to OTP verification page

                    else:
                        messages.error(request, 'Invalid login details. Please check your username/email and password.')
                        return redirect('login')

                except User.DoesNotExist:
                    messages.error(request, 'User not found. Please check your credentials or sign up.')
                    return redirect('login')

            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)

        except Exception as e:
            messages.error(request, 'An unexpected error occurred. Please try again.')
            print(f"Unexpected error during login: {e}")
            return redirect('login')

        except RemoteDisconnected:
            print("RemoteDisconnected error occurred during login.")
            messages.error(
                request,
                "There was a connection issue while processing your request. Please try again."
            )
            return redirect('login')

    return render(request, 'users/login.html', {'form': form})

def verify_otp(request):
    """Handle OTP verification"""
    print("Accessing OTP verification view...")  
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        try:
            otp = OTP.objects.get(user=request.user, otp=otp_code, is_verified=False)
            print(f"Attempting OTP verification for {request.user.username}.")  

            # Check if OTP has expired
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
    """Handle resending OTP with rate limit of 2 attempts within 10 minutes."""
    print("Accessing resend OTP view...")  
    
    if request.method == "POST":
        try:
            # Check if the user has attempted to resend OTP more than twice in the last 10 minutes
            recent_attempts = OTP.objects.filter(
                user=request.user,
                is_verified=False,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
            ).count()

            if recent_attempts >= 2:
                messages.error(request, 'You have reached the limit of 2 OTP resend attempts within 10 minutes. Please try again later.')
                print(f"User {request.user.username} reached OTP resend attempt limit.")
                return redirect('verify_otp')  # Redirect to OTP verification page

            # Attempt to fetch an existing OTP (that is not yet verified) for the user
            otp = OTP.objects.get(user=request.user, is_verified=False)

            if otp.is_expired():
                # If OTP expired, generate a new one and send it
                otp = create_and_send_otp(request.user)
                messages.success(request, 'A new OTP has been sent to your email.')
                print(f"A new OTP has been sent to {request.user.email}.")
            else:
                messages.error(request, 'Your OTP is still valid. Please use it before requesting a new one.')
                print(f"OTP for {request.user.username} is still valid.")
                
        except OTP.DoesNotExist:
            # If no valid OTP is found, generate a new one
            otp = create_and_send_otp(request.user)
            messages.success(request, 'A new OTP has been sent to your email.')
            print(f"No valid OTP found. Generated new OTP for {request.user.email}.")

    return redirect('verify_otp')  # Redirect to OTP verification page



# Password Reset
ATTEMPT_LIMIT = 3
RATE_LIMIT_DURATION = 3600  # 1 hour in seconds

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check rate limit
        cache_key = f"password_reset_attempts:{email}"
        last_attempt_time_key = f"{cache_key}:last_attempt_time"
        
        # Get current attempts and the last attempt time
        attempts = cache.get(cache_key, 0)
        last_attempt_time = cache.get(last_attempt_time_key)

        if last_attempt_time:
            elapsed_time = datetime.now() - last_attempt_time
            if elapsed_time.total_seconds() > RATE_LIMIT_DURATION:
                # Reset attempts after the rate limit period has passed
                attempts = 0
                cache.set(cache_key, attempts, RATE_LIMIT_DURATION)
        
        if attempts >= ATTEMPT_LIMIT:
            # Calculate remaining time
            remaining_time = RATE_LIMIT_DURATION - elapsed_time.total_seconds()
            minutes, seconds = divmod(int(remaining_time), 60)
            messages.error(request, f"Too many attempts. Please try again in {minutes} minutes and {seconds} seconds.")
            return redirect('password_reset')

        # Check if the email exists in the database
        try:
            user = User.objects.get(email=email)
            # Generate the reset URL and send the email if user exists
            reset_url = generate_reset_token_and_url(user, request)
            send_reset_email(user, reset_url)
        except User.DoesNotExist:
            # If user doesn't exist, still inform the user but apply rate limiting
            messages.success(request, "If an account with this email exists, a password reset email has been sent.")

        # Increment attempts and store the time of the last attempt
        cache.set(cache_key, attempts + 1, RATE_LIMIT_DURATION)
        cache.set(last_attempt_time_key, datetime.now(), RATE_LIMIT_DURATION)

        return redirect('password_reset')

    return render(request, 'users/password_reset_request.html')



def password_reset_confirm(request, uidb64, token):
    user = confirm_reset_token(uidb64, token)
    if not user:
        messages.error(request, "Invalid or expired token.")
        return redirect('password_reset')

    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password == password_confirm:
            # Reset and save the new password
            user.password = make_password(password)
            user.save()
            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'users/password_reset_confirm.html')


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
    print(f"Accessing profile view for user {request.user.username}.")
    
    # Check if the user's profile exists
    if not hasattr(request.user, 'profile'):
        print(f"User {request.user.username} has no profile. Creating one.")
        # Create the profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)
        print(f"Created profile for user {request.user.username}.")
    else:
        # Retrieve the profile if it exists
        profile = request.user.profile
        print(f"User profile details: {profile}")
    
    # Check if the user is active
    if not request.user.is_active:
        print(f"User {request.user.username}'s email is not verified.")
        messages.warning(request, 'Your account\'s email is yet verified.')
        return redirect('email_verification_request')  # Redirect to an appropriate page for inactive accounts

    # Pass the profile to the template
    context = {
        'profile': profile,
    }

    return render(request, 'users/profile.html', context)


def author_profile_view(request, username):
    print(f"Accessing profile view for author -> {username}.")
    # Fetch the user by username
    author = get_object_or_404(User, username=username)
    profile = author.profile  # Assuming a OneToOne relation exists with Profile
    return render(request, 'profile.html', {'profile': profile, 'author': author})


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
            redirect('email_sent', email=email)
        else:
            messages.info(request, 'Your email is already verified.')
        
        return redirect('profile')

    return render(request, 'users/email_verification_request.html')


@login_required
def edit_profile(request):
    """
    Allows the user to edit their profile information.
    """
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    # Debugging print statement for when the profile is fetched
    print(f"Accessing edit profile for user {user.username}. Profile: {profile}")

    if request.method == 'POST':
        # Create the forms with POST data
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        # Print form data for debugging
        print(f"User form data: {request.POST}")
        print(f"Form files: {request.FILES}")
        
        # Check if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save changes to the User model (including username)
            profile_form.save()  # Save changes to the Profile model
            
            # Print success message for debugging
            print(f"Profile updated for user {user.username}.")
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to the profile page after saving
        else:
            # Add error messages
            if user_form.errors:
                for field, error_list in user_form.errors.items():
                    for error in error_list:
                        messages.error(request, f"{field.capitalize()}: {error}")
            if profile_form.errors:
                for field, error_list in profile_form.errors.items():
                    for error in error_list:
                        messages.error(request, f"{field.capitalize()}: {error}")

            # Print form validation errors for debugging
            print(f"User form errors: {user_form.errors}")
            print(f"Profile form errors: {profile_form.errors}")
    else:
        # Initialize forms with current user and profile data
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'users/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})



@login_required
def settings_view(request):
    """
    Manages user settings such as email notifications, dark mode preferences, email, and password updates.
    """
    # Fetch or create user settings
    settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_settings':
            # Handle Email Notifications and Dark Mode together
            email_notifications = request.POST.get('email_notifications') == 'on'
            dark_mode = request.POST.get('dark_mode') == 'on'
            settings.email_notifications = email_notifications
            settings.dark_mode = dark_mode
            settings.save()
            messages.success(request, 'Settings have been updated.')

        elif action == 'change_email':
            new_email = request.POST.get('email')
            if new_email and new_email != request.user.email:
                try:
                    # Check if the email is already taken
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, 'Your email has been updated.')
                except ValidationError:
                    messages.error(request, 'The email address is already in use.')

        # Handle Password Change
        if action == 'change_password'and password_form.validate_on_submit():
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)  # Important to keep the user logged in
                messages.success(request, 'Your password has been updated.')

        return redirect('profile')  # Redirect to the profile page after saving settings

    # Password Change Form
    password_form = PasswordChangeForm(user=request.user)

    return render(request, 'users/settings.html', {
        'settings': settings,
        'password_form': password_form
    })

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

def recent_activities(request):
    """
    Displays a list of recent activities of the logged-in user.
    """
    # Example: You can retrieve activities from a model if you have one, or simulate recent activities.
    activities = [
        {"activity": "Created a new blog post.", "timestamp": "2024-12-20 10:00 AM"},
        {"activity": "Commented on a blog post.", "timestamp": "2024-12-19 03:30 PM"},
        {"activity": "Updated profile picture.", "timestamp": "2024-12-18 08:45 AM"},
    ]

    context = {
        'activities': activities
    }

    return render(request, 'users/recent_activities.html', context)

def my_blogs(request):
    """
    Displays all the blogs posted by the logged-in user.
    """
    # Retrieve blogs by the logged-in user
    blogs = Blog.objects.filter(author=request.user)

    context = {
        'blogs': blogs
    }

    return render(request, 'users/my_blogs.html', context)


def notifications(request):
    """
    Displays the notifications for the logged-in user.
    """
    # Retrieve notifications for the logged-in user, ordered by creation date
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    context = {
        'notifications': notifications
    }

    return render(request, 'users/notifications.html', context)

@login_required
def change_email(request):
    # Your email change logic here, such as sending a verification email
    if request.method == "POST":
        # Process the email change request
        new_email = request.POST['email']
        # Logic to verify email and send token can go here
        send_mail("Change your email", "Verification token", "no-reply@example.com", [new_email])
        return redirect('settings')  # Redirect back to settings after email change request
    
    return render(request, 'users/change_email.html')

@login_required
def manage_subscription(request):
    if request.method == "POST":
        subscription_type = request.POST.get('subscription_type')
        if subscription_type == 'monthly':
            duration = timedelta(days=30)
        elif subscription_type == 'annual':
            duration = timedelta(days=365)
        else:
            duration = None

        if duration:
            profile = request.user.profile
            profile.subscription_type = subscription_type
            profile.subscription_end = now() + duration
            profile.save()
            # Payment processing logic here
            return redirect('home')  # Redirect to your desired page
    
    return render(request, 'manage_subscription.html')
