from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
import logging
from users.models import OTP
from datetime import timedelta
from django.utils import timezone
import random
import string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model

User = get_user_model()



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



#Password reset utils functions
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings

TOKEN_EXPIRATION_MINUTES = 10  # Set token expiration time

User = get_user_model()

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
    Confirm if a password reset token is valid for a given user.
    """
    try:
        # Decode the user ID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Validate the token
        if default_token_generator.check_token(user, token):
            return user  # Return the user if token is valid
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    return None









# from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.core.mail import send_mail
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.utils import timezone
# from django.core.cache import cache
# from django.utils.translation import gettext_lazy as _  # For internationalization if needed
# from django.contrib.auth.hashers import make_password
# from datetime import datetime, timedelta
# from django.utils.encoding import force_str


# User = get_user_model()

# # Password Reset Rate Limiting
# ATTEMPT_LIMIT = 3
# RATE_LIMIT_DURATION = 3600  # 1 hour in seconds

# class ExpiringTokenGenerator(PasswordResetTokenGenerator):
#     def _get_timestamp(self, token):
#         """Retrieve the timestamp from the token."""
#         return token.split('-')[1]  # This assumes the timestamp is part of the token

#     def token_is_expired(self, user, token, expiration_minutes):
#         try:
#             timestamp = self._get_timestamp(token)
#             token_created_time = timezone.datetime.fromtimestamp(int(timestamp))
#             current_time = timezone.now()
#             return (current_time - token_created_time) > timedelta(minutes=expiration_minutes)
#         except Exception:
#             return True  # Treat invalid tokens as expired

# # Helper function to generate reset token and URL
# def generate_reset_token_and_url(user, request):
#     """
#     Generate a token and password reset URL for a given user.
#     """
#     token_generator = ExpiringTokenGenerator()
#     token = token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     timestamp = int(timezone.now().timestamp())  # Add current timestamp to the token
#     reset_url = request.build_absolute_uri(f'/users/password_reset_confirm/{uid}/{token}-{timestamp}/')
#     return reset_url


# # Helper function to send reset email
# def send_reset_email(user, reset_url):
#     """
#     Send the password reset email to the user.
#     """
#     subject = _('Password Reset Request')
#     message = (
#         f"Hi {user.username},\n\n"
#         f"We received a request to reset your password. You can reset it using the link below:\n"
#         f"{reset_url}\n\n"
#         f"This link expires in 10 minutes!\n\n"
#         f"If you didn't request this, please ignore this email."
#     )
#     send_mail(
#         subject,
#         message,
#         'from@example.com',  # Replace with your from email
#         [user.email],
#     )

# # Function to confirm the reset token
# def confirm_reset_token(uidb64, token):
#     """
#     Confirm if a password reset token is valid for a given user and check its expiration time.
#     """
#     try:
#         # Decode the user ID
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         User = get_user_model()  # Use the custom user model
#         user = User.objects.get(pk=uid)

#         # Validate the token and check expiration
#         token_generator = ExpiringTokenGenerator()
#         token_part, timestamp_part = token.rsplit('-', 1)  # Split the token and timestamp parts
#         if token_generator.check_token(user, token_part):  # Validate the token
#             if not token_generator.token_is_expired(user, token, 10):  # Expiration time set to 10 minutes
#                 return user
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         pass

#     return None




# from datetime import timedelta
# from django.utils.timezone import now

# TOKEN_EXPIRATION_MINUTES = 10  # Set token expiration time


# def generate_reset_token_and_url(user, request):
#     """
#     Generate a token and password reset URL for a given user.
#     """
#     token = default_token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     reset_url = request.build_absolute_uri(f'/users/password_reset_confirm/{uid}/{token}/')
#     return reset_url


# def send_reset_email(user, reset_url):
#     """
#     Send the password reset email to the user.
#     """
#     subject = 'Password Reset Request'
#     message = (
#         f"Hi {user.username},\n\n"
#         f"We received a request to reset your password. You can reset it using the link below:\n"
#         f"{reset_url}\n\n"
#         f"This link expires in 10 minutes!\n\n"
#         f"If you didn't request this, please ignore this email."
#     )
#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#     )


# def confirm_reset_token(uidb64, token):
#     """
#     Confirm if a password reset token is valid for a given user and check its expiration time.
#     """
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)

#         # Validate the token
#         if default_token_generator.check_token(user, token):
#             # Extract the timestamp from the token
#             timestamp = default_token_generator._num_seconds(default_token_generator.today())
#             token_created_time = timedelta(seconds=timestamp)
#             current_time = timedelta(seconds=int(now().timestamp()))
            
#             # Check if the token is within the expiration time
#             if (current_time - token_created_time) <= timedelta(minutes=TOKEN_EXPIRATION_MINUTES):
#                 return user
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         pass

#     return None

# from django.contrib.auth import get_user_model
# from django.utils.http import urlsafe_base64_decode
# from django.utils.timezone import now
# from datetime import timedelta
# from django.contrib.auth.tokens import PasswordResetTokenGenerator

# # Custom token generator
# class ExpiringTokenGenerator(PasswordResetTokenGenerator):
#     def token_is_expired(self, user, token, expiration_minutes):
#         try:
#             # Decode the token timestamp
#             timestamp = self._decode_timestamp(self._get_timestamp(token))
#             token_created_time = timedelta(seconds=timestamp)
#             current_time = timedelta(seconds=int(now().timestamp()))
#             # Check if the token is expired
#             return (current_time - token_created_time) > timedelta(minutes=expiration_minutes)
#         except Exception:
#             return True  # Treat invalid tokens as expired

# # Use the custom generator
# token_generator = ExpiringTokenGenerator()

# # Token expiration time in minutes
# TOKEN_EXPIRATION_MINUTES = 10

# def confirm_reset_token(uidb64, token):
#     """
#     Confirm if a password reset token is valid for a given user and check its expiration time.
#     """
#     try:
#         # Decode the user ID
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         User = get_user_model()  # Use the custom user model
#         user = User.objects.get(pk=uid)

#         # Validate the token and check expiration
#         if token_generator.check_token(user, token):
#             if not token_generator.token_is_expired(user, token, TOKEN_EXPIRATION_MINUTES):
#                 return user
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         pass

#     return None
