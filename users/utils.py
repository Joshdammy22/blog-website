from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .models import *
from django.core.exceptions import ValidationError


def generate_verification_token():
    """
    Generates a unique verification token.
    """
    return get_random_string(length=64)


def send_verification_email(request, user):
    """
    Sends an email verification link to the user.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    token = generate_verification_token()
    profile.verification_token = token
    profile.save()

    # Generate verification link
    current_site = get_current_site(request)
    verification_url = request.build_absolute_uri(
        reverse('email_verification', args=[token])
    )
    
    # Email subject and message
    subject = f"Verify your email address - {settings.APP_NAME}"
    message = f"""
    Hi {user.username},

    Please verify your email by clicking the link below:

    {verification_url}

    Thank you!
    {settings.APP_NAME}
    """
    
    # Send email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


#Functions for user log in otp generation functionality
# Function to generate OTP
def generate_otp(user):
    otp = OTP.objects.create(user=user)
    otp.generate_otp()
    return otp

# Function to check if OTP rate limit is exceeded
def is_rate_limited(user):
    """Check if the user has exceeded the OTP request limit (3 requests per 5 minutes)"""
    time_limit = timezone.now() - timedelta(minutes=5)
    recent_otp_requests = OTP.objects.filter(user=user, created_at__gte=time_limit)
    if recent_otp_requests.count() >= 3:
        return True
    return False

# Function to handle requesting OTP with rate limiting
def request_otp(user):
    """Generate an OTP if the user hasn't exceeded the rate limit"""
    if is_rate_limited(user):
        raise ValidationError("You have exceeded the number of OTP requests. Please try again later.")
    return generate_otp(user)
