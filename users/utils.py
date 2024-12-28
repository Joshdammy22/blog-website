from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
import logging
from users.models import OTP
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import random
import string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

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

#Functions for handling user login with token verification
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


from datetime import timedelta
from django.utils.timezone import now

TOKEN_EXPIRATION_MINUTES = 10  # Set token expiration time


def generate_reset_token_and_url(user, request):
    """
    Generate a token and password reset URL for a given user.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(f'/users/password_reset_confirm/{uid}/{token}/')
    return reset_url


def send_reset_email(user, reset_url):
    """
    Send the password reset email to the user.
    """
    subject = 'Password Reset Request'
    message = (
        f"Hi {user.username},\n\n"
        f"We received a request to reset your password. You can reset it using the link below:\n"
        f"{reset_url}\n\n"
        f"This link expires in 10 minutes!\n\n"
        f"If you didn't request this, please ignore this email."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


def confirm_reset_token(uidb64, token):
    """
    Confirm if a password reset token is valid for a given user and check its expiration time.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Validate the token
        if default_token_generator.check_token(user, token):
            # Extract the timestamp from the token
            timestamp = default_token_generator._num_seconds(default_token_generator.today())
            token_created_time = timedelta(seconds=timestamp)
            current_time = timedelta(seconds=int(now().timestamp()))
            
            # Check if the token is within the expiration time
            if (current_time - token_created_time) <= timedelta(minutes=TOKEN_EXPIRATION_MINUTES):
                return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    return None
