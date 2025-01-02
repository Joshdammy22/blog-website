from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model, login
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Allow signup based on specific logic.
        """
        if request.path.startswith('/accounts/google/'):
            # Allow signups via Google OAuth
            return True
        return super().is_open_for_signup(request)

    def is_email_verified(self, request, email):
        """
        Exempt admin users from email verification.
        """
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.is_superuser or user.is_staff:
                return True
        except User.DoesNotExist:
            pass
        return super().is_email_verified(request, email)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle pre-login logic for social accounts.
        """
        email = sociallogin.user.email
        if email:
            User = get_user_model()
            try:
                # Check if a user with this email already exists
                existing_user = User.objects.get(email=email)

                # If the user exists and is not linked to the social account, connect them
                if not sociallogin.is_existing:
                    sociallogin.connect(request, existing_user)

                # Set the backend to the Allauth backend
                existing_user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
                login(request, existing_user)
                messages.success(request, 'Login successful!')

                # Redirect to the home page after login
                raise ImmediateHttpResponse(HttpResponseRedirect('/'))
            except User.DoesNotExist:
                # If the email does not exist, proceed with the normal flow
                pass
