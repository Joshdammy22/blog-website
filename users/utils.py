from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
import logging
from users.models import OTP
# Logger setup
logger = logging.getLogger(__name__)

# Serializer for generating and validating tokens
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_verification_token(email):
    """
    Generates a unique time-sensitive verification token for the given email.
    """
    return serializer.dumps(email, salt=settings.SECURITY_SALT)

def validate_verification_token(token, max_age=86400):
    """
    Validates a verification token and checks if it has expired.
    """
    try:
        email = serializer.loads(token, salt=settings.SECURITY_SALT, max_age=max_age)
        return email
    except SignatureExpired:
        logger.warning("Verification token has expired.")
        return None
    except BadData:
        logger.error("Invalid verification token.")
        return None

def send_verification_email(request, user):
    """
    Sends an email verification link to the user.
    """
    token = generate_verification_token(user.email)

    # Generate verification link
    current_site = get_current_site(request)
    verification_url = request.build_absolute_uri(
        reverse('email_verification', args=[token])
    )

    subject = f"Verify your email address - {settings.APP_NAME}"
    message = generate_verification_message(user, verification_url)

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        logger.info(f"Verification email sent to {user.email}.")
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        raise Exception('Error sending verification email.')

def generate_verification_message(user, verification_url):
    """
    Generates the email message content for verification.
    """
    return f"""
    Hi {user.username},

    Please verify your email by clicking the link below:

    {verification_url}

    This link is valid for 24 hours.

    Thank you!
    {settings.APP_NAME}
    """


import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP

def generate_otp(length=6):
    """Generate a random OTP with the specified length (default 6 digits)."""
    otp = ''.join(random.choices(string.digits, k=length))  # Generate a random 6-digit OTP
    return otp

def create_and_send_otp(user):
    """Generate OTP for a user, set expiration time of 10 minutes, and send OTP via email."""
    # Generate OTP
    otp_code = generate_otp()
    
    # Set expiration time to 10 minutes from now
    expiration_time = timezone.now() + timedelta(minutes=10)
    
    # Create OTP object and save to the database
    otp = OTP.objects.create(user=user, otp=otp_code, expires_at=expiration_time, is_verified=False)
    
    # Send OTP to user's email
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp.otp}\nIt will expire in 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL  # Use default from email set in settings
    
    # Send OTP email
    send_mail(
        subject,
        message,
        from_email,
        [user.email],
        fail_silently=False,
    )

    return otp
