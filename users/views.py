from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import Profile, CustomUser
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
from urllib.error import URLError

# Create logger
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
                    # Customize error messages based on field and error
                    if field == 'password1':
                        if "too common" in error:
                            messages.error(request, "This password is too common. Please choose a stronger one.")
                        elif "too short" in error:
                            messages.error(request, "The password must be at least 8 characters long.")
                        elif "entirely numeric" in error:
                            messages.error(request, "The password cannot be entirely numeric. Please add letters.")
                        elif "password is too similar" in error:
                            messages.error(request, "This password is too similar to your username or personal information.")
                        else:
                            messages.error(request, f"Password: {error}")
                    elif field == 'password2':
                        if "match" in error:
                            messages.error(request, "The passwords do not match. Please ensure both passwords are the same.")
                    elif field == 'username':
                        messages.error(request, f"Username: {error}")
                    elif field == 'email':
                        messages.error(request, f"Email: {error}")
                    else:
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
        user = CustomUser.objects.get(email=email)

        # Update the user's active status and profile email verification status
        user.is_active = True
        user.save()

        # Ensure the Profile exists and update email_verified
        profile, created = Profile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()

        messages.success(request, 'Your email has been verified successfully. You can now log in.')
        return redirect('login')
    except CustomUser.DoesNotExist:
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
        user = CustomUser.objects.get(email=email, is_active=False)
        send_verification_email(request, user)
        messages.success(request, f"A new verification email has been sent to {email}.")
    except CustomUser.DoesNotExist:
        messages.error(request, "No inactive account found with this email address.")
    except Exception as e:
        logger.error(f"Error resending verification email: {e}")
        messages.error(request, "An error occurred while resending the email. Please try again later.")

    return redirect("email_sent", email=email)


# User login
def login_view(request):
    # Redirect if the user is already authenticated
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Redirecting to home...')
        return redirect('home')

    form = UserLoginForm(data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                username_or_email = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                print(f"Username or Email: {username_or_email}")

                # Authenticate the user using the custom authentication logic
                user = authenticate(request, username=username_or_email, password=password)

                if user:
                    # Check if the user is active
                    if not user.is_active:
                        messages.error(request, 'Your account is inactive. Please verify your email or contact support.')
                        return redirect('login')
                    
                    # Generate OTP and send it
                    otp = create_and_send_otp(user)

                    # Save user ID in session for OTP verification
                    request.session['temp_user_id'] = user.id

                    messages.info(request, 'An OTP has been sent to your email. Please verify.')
                    return redirect('verify_otp')
                else:
                    messages.error(request, 'Invalid login details. Please check your username/email and password.')
            except ValidationError as e:
                # Handle validation errors raised from the form or authentication process
                print(f"Validation error: {e}")
                messages.error(request, str(e))
            except RemoteDisconnected:
                print("RemoteDisconnected error occurred during login.")
                messages.error(
                    request,
                    "There was a connection issue while processing your request. Please try again."
                )
            except Exception as e:
                # Catch any other unexpected errors
                print(f"Unexpected error: {e}")
                messages.error(request, 'An unexpected error occurred. Please try again later.')
            except URLError as e:
                messages.error(request, "A network error occurred. Please check your connection and try again.")
                print(f"URLError: {e}")
        else:
            # Handle form errors and display them to the user
            print(f"Form is not valid. Errors: {form.errors}")  # Debugging purposes
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    return render(request, 'users/login.html', {'form': form})


from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend

def verify_otp(request):
    """Handle OTP verification"""
    print("Accessing OTP verification view...")

    if 'temp_user_id' not in request.session:
        messages.error(request, 'You must be logged in first.')
        return redirect('login')

    user_id = request.session.get('temp_user_id')
    user = CustomUser.objects.get(id=user_id)

    # Explicitly set the backend to CustomUserAuthenticationBackend
    user.backend = 'users.backends.CustomUserAuthenticationBackend'

    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        try:
            otp = OTP.objects.get(user=user, otp=otp_code, is_verified=False)
            print(f"Attempting OTP verification for {user.username}.")

            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                print(f"OTP expired for {user.username}.")
                return redirect('login')

            otp.is_verified = True
            otp.save()

            # Login the user after successful OTP verification
            login(request, user)
            messages.success(request, 'OTP verified successfully. You are now logged in!')
            print(f"OTP verified successfully for {user.username}.")
            return redirect('home')

        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP')
            print(f"Invalid OTP entered for {user.username}.")

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


# Password reset request view with rate-limiting
from django.contrib.auth import get_user_model
User = get_user_model()

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
            pass

        messages.success(request, "If an account with this email exists, a password reset email has been sent.")

        # Increment attempts and store the time of the last attempt
        cache.set(cache_key, attempts + 1, RATE_LIMIT_DURATION)
        cache.set(last_attempt_time_key, datetime.now(), RATE_LIMIT_DURATION)

        return redirect('password_reset')

    return render(request, 'users/password_reset_request.html')

# Password reset confirm view
def password_reset_confirm(request, uidb64, token):
    user = confirm_reset_token(uidb64, token)
    
    if not user:
        messages.error(request, "Invalid or expired token.")
        return redirect('password_reset')
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            # Save the new password
            user.password = make_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')
        else:
            # If form is invalid, handle field-specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'new_password1':
                        if "too common" in error:
                            messages.error(request, "This password is too common. Please choose a stronger one.")
                        elif "too short" in error:
                            messages.error(request, "The password must be at least 8 characters long.")
                        elif "entirely numeric" in error:
                            messages.error(request, "The password cannot be entirely numeric. Please add letters.")
                        elif "password is too similar" in error:
                            messages.error(request, "This password is too similar to your username or personal information.")
                        else:
                            messages.error(request, f"New Password: {error}")
                    elif field == 'new_password2':
                        if "match" in error:
                            messages.error(request, "The passwords do not match. Please ensure both passwords are the same.")
                    else:
                        messages.error(request, f"{field.capitalize()}: {error}")
    else:
        # Initialize the form if it's a GET request
        form = CustomPasswordChangeForm(user=user)

    return render(request, 'users/password_reset_confirm.html', {'form': form})


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


@login_required
def author_profile_view(request, username):
    print(f"Accessing profile view for author -> {username}.")
    
    # Fetch the user by username
    author = get_object_or_404(User, username=username)
    profile = author.profile  # Assuming a OneToOne relation exists with Profile
    
    # Get all published blogs by this author
    blogs = Blog.objects.filter(author=author, status=1).order_by('-created_at')  # Only published blogs
    
    # Check if the current user follows the author
    is_following = Follow.objects.filter(follower=request.user, followee=author).exists()

    return render(request, 'profile.html', {
        'profile': profile,
        'author': author,
        'is_following': is_following,  # Pass the follow status
        'blogs': blogs,  # Pass the blogs to the template
    })




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
    pass

# User Blog Interaction View
@login_required
def user_blog_interactions(request):
    pass

def recent_activities(request):
    pass

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

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from blog.models import Notification

@login_required
def fetch_notifications(request):
    # Fetch unseen notifications for the logged-in user
    unseen_notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    
    notifications_data = []
    for n in unseen_notifications:
        if n.notification_type == 'follow':
            message = f"{n.sender.username} started following you."
            url = "/profile/"  # Adjust the URL to the user's profile page
        elif n.notification_type == 'reaction' or n.notification_type == 'comment':
            message = f"{n.sender.username} {n.get_notification_type_display()} your post: {n.blog.title}" if n.blog else ""
            url = f"/blog/{n.blog.id}" if n.blog else "/"
        else:
            message = "You have a new notification."
            url = "/"
        
        notifications_data.append({
            "message": message,
            "url": url,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return JsonResponse({
        "unseen_count": unseen_notifications.count(),
        "notifications": notifications_data
    })


@login_required
def mark_notifications_as_read(request):
    if request.method == "POST":
        # Mark all unseen notifications as read
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




@login_required
def notifications(request):
    """
    Displays the notifications for the logged-in user and marks them as read.
    """
    # Retrieve notifications for the logged-in user, ordered by creation date
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    # Mark unread notifications as read
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

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

# @login_required
# def manage_subscription(request):
#     if request.method == "POST":
#         subscription_type = request.POST.get('subscription_type')
#         if subscription_type == 'monthly':
#             duration = timedelta(days=30)
#         elif subscription_type == 'annual':
#             duration = timedelta(days=365)
#         else:
#             duration = None

#         if duration:
#             profile = request.user.profile
#             profile.subscription_type = subscription_type
#             profile.subscription_end = now() + duration
#             profile.save()
#             # Payment processing logic here
#             return redirect('home')  # Redirect to your desired page
    
#     return render(request, 'manage_subscription.html')



from django.shortcuts import render
from blog.models import *
from django.core.paginator import Paginator

def analytics_page(request):
    # Get all blogs by the logged-in user, ordered by creation date
    blogs = Blog.objects.filter(author=request.user).order_by('-created_at')

    # Debugging print: List of blogs retrieved
    print("Blogs Retrieved: ", blogs)

    # Pagination: Display 5 blogs per page
    paginator = Paginator(blogs, 5)  # Show 5 blogs per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_obj = paginator.get_page(page_number)

    # Gather analytics data for each blog
    blog_analytics = []
    for blog in page_obj:
        reactions_data = {
            'like': blog.get_reaction_count('like'),
            'love': blog.get_reaction_count('love'),
            'haha': blog.get_reaction_count('haha'),
            'wow': blog.get_reaction_count('wow'),
            'applaud': blog.get_reaction_count('applaud')
        }

        # Calculate total reactions
        total_reactions = sum(reactions_data.values())

        # Total comments and reads
        comments_count = blog.comments.count()
        total_reads = blog.read_count

        # Debugging print: Key metrics for each blog
        print(f"Blog: {blog.title}")
        print(f"Reads: {total_reads}, Comments: {comments_count}, Total Reactions: {total_reactions}")

        # Add data to the list
        blog_analytics.append({
            'blog': blog,
            'reactions': reactions_data,
            'comments_count': comments_count,
            'total_reads': total_reads,
            'chart_data': [total_reads, comments_count, total_reactions]  # Format for chart
        })

    # Total counts for the header
    total_blogs = blogs.count()
    total_reads = sum(blog['total_reads'] for blog in blog_analytics)
    total_engagements = sum(blog['comments_count'] + sum(blog['reactions'].values()) for blog in blog_analytics)

    # Debugging print: Total values
    print("Total Blogs: ", total_blogs)
    print("Total Reads: ", total_reads)
    print("Total Engagements: ", total_engagements)

    return render(request, 'users/analytics.html', {
        'blogs': blog_analytics,
        'total_blogs': total_blogs,
        'total_reads': total_reads,
        'total_engagements': total_engagements,
        'page_obj': page_obj,  # Pass the pagination object to the template
    })
