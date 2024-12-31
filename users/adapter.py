from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Disable signup completely if needed
        return False

    def is_email_verified(self, user):
        """
        Override this method to exempt admin users from email verification.
        """
        if user.is_superuser or user.is_staff:
            return True
        return super().is_email_verified(user)
